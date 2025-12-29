import os, shutil
from playwright.sync_api import sync_playwright

# UPDATES: account for multiple page results, download main image



class Wiki_Snippet_Saver:

    def __init__(self, main_link) -> None:
        self.ver = f"1.0.0"
        self.main_link = main_link
        self.playwright = sync_playwright().start()
        self.broswer = self.playwright.chromium.launch(headless=True)
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        self.wiki_page = self.broswer.new_page(user_agent=self.user_agent)
        os.makedirs('Saved-Text', exist_ok=True)
        


    def title(self):
        title = f"- Wiki Snippet Saver v.{self.ver} -"
        return ("\n" + title +"\n" + "=" * len(title))

    def grab_snippet(self):
        while True:
            search_term = str(input('Please enter wikipedia search term: (enter \"CANCEL SEARCH\" to exit)\n> '))
            if search_term:
                return search_term
            print(f"Invalid search term. Please try again.")
    
    def check_span(self):
        return self.wiki_page.locator('li#ca-view span').all()
    
    def redirect(self, term, link_dict):

        print(f"-\n{term} may refer to:")

        command_dict = {}
        exit_key = 1

        for i, key in enumerate(link_dict, 1):
            print(f"{i} - {key}")
            command_dict[i] = link_dict[key]
            exit_key += 1
        print(f"{exit_key} - Return..")
        

        while True:

            command = int(input("> "))

            if command in command_dict.keys():
                self.search(command_dict[command], True)
                break
            elif command == exit_key:
                return
            else:
                print(f"Invalid command. Please try again.")

        


    def search(self, term: str, redirect=False):

        if redirect:
            self.download_link = f"https://en.wikipedia.org{term}"
        else:
            term = term.title()
            self.download_link = f'{self.main_link}{term}'

        self.wiki_page.goto(self.download_link)

        if not self.check_span():
            print(f"-\nWikipedia does not have an article with this exact name.\n Please search for {term} in Wikipedia to check for alternative titles or spellings.\n-")
            return
        
        header_loc = self.wiki_page.locator('header h1')
        
        main_body = self.wiki_page.locator('div.mw-parser-output')

        text_locator = main_body.locator('h2, p, ul li')

        main_text = [text.strip().strip('\n') for text in text_locator.all_inner_texts() if text.strip().strip('\n')]

        header = header_loc.all_inner_texts()[0]

        if len(main_body.locator('p').all_inner_texts()) == 1:
            link_text = self.wiki_page.locator('div.mw-parser-output ul li')
            l_dict = {}

            for i in range(link_text.count()):
                first_a = link_text.nth(i).locator('a').first
                l_dict[link_text.all_inner_texts()[i]] = first_a.get_attribute('href')

            self.redirect(term, l_dict)

        else:

            print("\n" + header +"\n" + "=" * len(header))
            for i in range(3):
                print(main_text[i] + "\n")

            while True:
                choice = str(input('-\nWould you like to download the entire text? (Y/N)\n> '))
                if choice.upper() in ["Y", "YES"]:

                    self.download_page(main_text, header)
                    break
                elif choice.upper() in ["N", "NO"]:
                    print("-")
                    return
                else:
                    print(f"-\nInvalid command. Please try again.\n-")
                    

    def download_page(self, text, doc_name):
        os.makedirs(f'Saved-Text\\{doc_name} - Wikipedia', exist_ok=True)

        with open(f'Saved-Text\\{doc_name} - Wikipedia\\{doc_name}.txt', 'w+', encoding='UTF-8') as doc_file:
            for para in text:
                doc_file.write(para + "\n" + "\n")

        self.wiki_page.pdf(path=f'Saved-Text\\{doc_name} - Wikipedia\\{doc_name}.pdf')
        print('Text document(s) created.\n-')
        
    def delete_snippet(self, all=False):

        dir_list = os.listdir("Saved-Text")

        if not dir_list:
            print(f"There are no folders to delete.")
            return
        
        dir_dict = {}
        
        for i, dir in enumerate(dir_list, 1):
            dir_dict[str(i)] = dir
            
        if not all:
            while True:
                exit_key = 1
                print(f"Please select which folder to delete:\n-")
                for key, value in dir_dict.items():
                    print(f"{key} - {value}")
                    exit_key += 1

                print(f"{exit_key} - Return..")
                
                command = str(input("> "))

                if command in dir_dict.keys():
                    shutil.rmtree(f"Saved-Text\\{dir_dict[command]}")
                    print(f"-\nFolder deleted.")
                    print("-")
                    break
                elif command == str(exit_key):
                    break
                    
                else:
                    print(f"-\nInvalid command. Please try again.\n-")
                    continue
        else:
            while True:
                command = str(input(f"CONFIRM deletion of all data (Y/N):"))

                if command.upper() in ["Y", "YES"]:
                    for i in range(1, len(dir_dict) + 1):
                        shutil.rmtree(f"Saved-Text\\{dir_dict[str(i)]}")
                    print(f"-\nAll folders deleted.")
                    break

                elif command.upper() in ["N", "NO"]:
                    return
                else:
                    print(f"-\nInvalid command. Please try again.\n-")

    def menu_select(self):
        menu_options = {"1": "Search Snippet..",
                        "2": "Delete Snippet..",
                        "3": "Delete All Snippets..",
                        "4": "Exit.."}
        
        while True:
            for key, value in menu_options.items():
                print(f"{key} - {value}")

            command = str(input("> "))

            if command in menu_options.keys():
                print("-")
                return int(command)
            else:
                print(f"-\nInvalid command. Please try again.\n-")
                continue

    def exec(self):
        while True:
            print(self.title())
            menu_command = self.menu_select()
            if menu_command == 1:
                while True:
                    search_term = self.grab_snippet()
                    if search_term != 'CANCEL SEARCH':
                        self.search(search_term)
                    else:
                        break
            elif menu_command == 2:
                self.delete_snippet()
            elif menu_command == 3:
                self.delete_snippet(True)
            elif menu_command == 4:
                break

wss = Wiki_Snippet_Saver('https://en.wikipedia.org/wiki/')

wss.exec()