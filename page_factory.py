import Page1
import DefaultPage


class PageFactory():

    def get_page_instance(self, page_type):
        if (page_type == 'TYPE_1'):  # 頁面命名的方式可能要再想，類似 English 或是 type1
            return Page1()
        else:
            return DefaultPage()
