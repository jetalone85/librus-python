class Inbox:
    """
    The Inbox class is responsible for fetching, sending, and processing messages from an API.

    Attributes:
        api (object): An instance of the API class used to make requests.
    """

    def __init__(self, api):
        """
        The constructor for the Inbox class.

        Parameters:
            api (object): An instance of the API class.
        """

        self.api = api

    def _get_confirm_message(self, soup):
        """
        Extracts the confirmation message from the HTML response.

        Parameters:
            soup (bs4.BeautifulSoup): A BeautifulSoup object containing the HTML of the page.

        Returns:
            str: The confirmation message.

        Raises:
            Exception: If no confirmation message is found.
        """

        message = soup.find("div", {"class": "green container"}).get_text(strip=True)
        if not message:
            raise Exception("No confirmation message found")
        return message

    def get_message(self, folder_id, message_id):
        """
        Fetches and processes a specific message.

        Parameters:
            folder_id (int): The ID of the folder containing the message.
            message_id (int): The ID of the message to fetch.

        Returns:
            dict: A dictionary containing the message data.

        Raises:
            ValueError: If access is denied or the message content could not be found.
        """

        url = f"wiadomosci/1/{folder_id}/{message_id}"
        soup = self.api.make_request('GET', url, parse_html=True)

        # Check for access issues directly
        if "Brak dostępu" in soup.text or "Loguj" in soup.text:
            raise ValueError("Access denied. Please check your credentials and permissions.")

        row = soup.select_one("table.stretch.container-message td.message-folders + td")
        if row is None:
            raise ValueError(
                "The specified message content could not be found. Please check the page structure or URL.")

        table = row.find("table", recursive=False)
        if table is None:
            raise ValueError("No table found under the specified row. Please check the HTML structure.")

        header = self.api.map_table_values(table, ["user", "title", "date"])

        # Attachment handling
        attachments = []
        for link in row.find_all("img", src=lambda x: x and "filetype" in x):
            name = link.find_parent("a").get_text(strip=True)
            path = link.find_parent("a")["onclick"].split('"')[1].replace("\\", "").strip("/")
            attachments.append({'name': name, 'path': path})

        return {
            "title": header.get("title", ""),
            "url": url,
            "id": message_id,
            "folder_id": folder_id,
            "date": header.get("date", ""),
            "user": header.get("user", ""),
            "content": row.find("div", class_="container-message-content").get_text(strip=True),
            "html": str(row.find("div", class_="container-message-content")),
            "read": "NIE" not in row.find("td", class_="left").get_text(strip=True),
            "files": attachments
        }

    def remove_message(self, message_id):
        """
        Removes a specific message.

        Parameters:
            message_id (int): The ID of the message to remove.

        Returns:
            str: The confirmation message.
        """

        data = {'tak': 'Tak', 'id': 1, 'Wid': message_id, 'poprzednia': 6}
        response = self.api.make_request('POST', 'wiadomosci', data=data, parse_html=True)
        return self._get_confirm_message(response)

    def send_message(self, user_id, title, content):
        """
        Sends a message to a specific user.

        Parameters:
            user_id (int): The ID of the user to send the message to.
            title (str): The title of the message.
            content (str): The content of the message.

        Returns:
            str: The confirmation message.
        """

        self.api.make_request('GET', 'wiadomosci/2/5', parse_html=True)
        data = {
            'DoKogo': user_id,
            'temat': title,
            'tresc': content,
            'poprzednia': 6,
            'wyslij': 'Wy%C5%9Blij'
        }
        response = self.api.make_request('POST', 'wiadomosci/5', data=data, parse_html=True)
        return self._get_confirm_message(response)

    def list_receivers(self, group):
        """
        Lists all receivers in a specific group.

        Parameters:
            group (int): The ID of the group.

        Returns:
            list: A list of dictionaries containing the receiver data.
        """

        response = self.api.make_request('POST', 'wiadomosci/1/5', data={'adresat': group}, parse_html=True)
        receivers = []
        for row in response.select("td.message-recipients table.message-recipients-detail tr[class*='line']"):
            id_val = row.find("input", {"name": "DoKogo[]"}).get('value')
            user = row.find("label").get_text(strip=True)
            receivers.append({"id": int(id_val), "user": user})
        return receivers

    def list_inbox(self, folder_id):
        """
        Lists all messages in a specific folder.

        Parameters:
            folder_id (int): The ID of the folder.

        Returns:
            list: A list of dictionaries containing the message data.
        """

        soup = self.api.make_request('GET', f"wiadomosci/{folder_id}", parse_html=True)
        messages = []
        for row in soup.select("table.container-message table.decorated.stretch tbody tr"):
            children = row.find_all("td")
            messages.append({
                "id": int(children[3].find("a")['href'].split('/')[4]),
                "user": children[2].get_text(strip=True),
                "title": children[3].get_text(strip=True),
                "date": children[4].get_text(strip=True),
                "read": "font-weight: bold;" not in children[2].get("style", "")
            })
        return messages

    def list_announcements(self):
        """
        Lists all announcements.

        Returns:
            list: A list of dictionaries containing the announcement data.
        """

        soup = self.api.make_request('GET', "ogloszenia", parse_html=True)
        announcements = []
        for row in soup.select("div#body div.container-background table.decorated"):
            cols = row.find_all("td")
            announcements.append({
                "title": row.find("thead").get_text(strip=True),
                "user": cols[1].get_text(strip=True),
                "date": cols[2].get_text(strip=True),
                "content": cols[3].get_text(strip=True)
            })
        return announcements
