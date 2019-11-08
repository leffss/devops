from django.urls import URLPattern


def get_all_urls(patterns, pre_fix, result):
    """
    递归获取 django 所有路由
    :param patterns:
    :param pre_fix:
    :param result:
    :return:
    """
    for item in patterns:
        part = item.pattern.regex.pattern.strip("^$")
        if isinstance(item, URLPattern):
            result.append(pre_fix + part)
        else:
            get_all_urls(item.url_patterns, pre_fix + part, result=result)
    return result


if __name__ == '__main__':
    from devops import urls
    for i in get_all_urls(urls.urlpatterns, pre_fix="/", result=[]):
        print(i)
