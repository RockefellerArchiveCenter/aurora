class PageTitleMixin(object):
    """Sets the page_title key in view data.
    On views where this mixin is added, page titles can be set either by providing
    a page_title attribute or a get_page_title method.
    """

    def get_page_title(self, context):
        return getattr(self, "page_title", "Default Page Title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title(context)
        return context
