from page import Page 


class PageFactory():

    def __init__(self, config):
        self.config = config

    def get_page_instance(self, page_type, ip):
        if (page_type == 'TYPE_1'):  # 頁面命名的方式可能要再想，類似 English 或是 type1
            return Page(self.config, page_type, ip)
