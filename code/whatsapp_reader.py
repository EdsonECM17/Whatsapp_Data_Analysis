import re
import pandas as pd

from typing import List

class WhatsappReader:
    """
    Class to read and pre-process a whatsapp chat txt file.
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def __clean_whatsapp_text(chat_text:str) -> str:
        """Clean specific content of the entire Whatsapp textfile.

        Args:
            chat_text (str): String of Whatsapp chat.

        Returns:
            str: String with replacement changes.
        """
        chat_text_aj = chat_text.replace("\xa0","")
        chat_text_aj = chat_text_aj.replace("\u200e","")
        chat_text_aj = chat_text_aj.replace(" (archivo adjunto)","")
        return chat_text_aj

    @staticmethod
    def __clean_message(message: str) -> str:
        """Clean message content.

        Args:
            message (str): Message sentence.

        Returns:
            str: Message content after cleaning.
        """
        # Remove symbols
        # removed_characters = message.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
        removed_characters = message
        # Clean repeated spaces
        removed_double_spaces = re.sub(' +', ' ', removed_characters)
        # Clean removed and traling spaces
        message_striped = removed_double_spaces.strip()
        # Add termination to files
        message_aj = message_striped.replace(" webp", ".webp")
        message_aj = message_aj.replace(" jpg", ".jpg")
        message_aj = message_aj.replace(" mp3", ".mp3")
        return message_aj

    @staticmethod
    def __starts_with_dt(line:str) -> bool:
        """Identifies if there is a timestamp in the message line

        Args:
            line (str): Line of whatsapp chat textfile.

        Returns:
            bool: Result of evaluation.
        """
        # patron = '^[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+\s[a-zA-Z].\s[a-zA-Z].\s-'
        patron = '^[0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+\s[a-zA-Z].[a-zA-Z].\s-'
        result = re.match(patron, line)
        if result:
            return True
        else:
            return False

    @staticmethod
    def __decompose_std_message(line:str) -> List[str]:
        """
        Separated message line into sections (datetime, author and message content).

        Args:
            line (str): Line of chat text file.

        Returns:
            List[str]: Filtered content of line in chat text.
        """
        # author init_row
        dt_msg_str = None
        author_str = None
        message_str = None
        # Separate author and message from date if there is date
        splitted_line: List[str] = line.split(' - ')
        # Obtener fecha y hora
        dt_msg_str = splitted_line[0]
        dt_msg_str = dt_msg_str.replace("p.m.","PM")
        dt_msg_str = dt_msg_str.replace("a.m.","AM")
        # Concat author and message
        sended_data: str = " - ".join(splitted_line[1:])
        # Split author
        splited_sended_data: List[str] = sended_data.split(": ")
        # Get author and message body
        if len(splited_sended_data)> 1: #Check if author
            # Ignore data after a comma if exist
            author_str = splited_sended_data[0].split(", ")[0] 
            message_str = ": ".join(splited_sended_data[1:])
        else:
            message_str=splited_sended_data[0]
            # author_str = "System"
        # Create content list
        content_list = [dt_msg_str, author_str, message_str]
        return content_list        

    def read_file(self, file_path: str):
        """
        Read text file and turn data into a dataframe.
        Columns are: [datetime, author, message]

        Args:
            file_path (str): Path of the text file.

        Returns:
            Dataframe: Chat table.
        """
        message_list = []
        chat = open(file_path, encoding="utf-8")
        chat_text = chat.read()
        # Clean str
        chat_text = self.__clean_whatsapp_text(chat_text)
        # Get data of each line
        for line in chat_text.split("\n"): 
            if line != "":
                if self.__starts_with_dt(line):
                    message_data = self.__decompose_std_message(line)
                else: 
                    message_data = [None] * 2 + [line]
                #Clean message
                message_data[-1] = self.__clean_message(message_data[-1])
                #Store data in list of list
                message_list.append(message_data)
        # Create dataframe
        chat_df = pd.DataFrame(message_list, columns=['Datetime', 'Author', 'Message'])
        # Change Date to datetime object
        chat_df["Datetime"] = pd.to_datetime(chat_df["Datetime"], format="%d/%m/%Y %I:%M %p")
        # Fill None values
        chat_df.fillna(method="ffill", inplace=True)
        # Delete system messages
        chat_df.dropna(inplace=True)
        chat_df.reset_index(drop=True, inplace=True)
        return chat_df
