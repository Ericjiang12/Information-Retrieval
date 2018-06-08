from django.http import HttpResponse
from django.template import loader
from search import handle_query


def result(request):
    raw_query = request.GET.get('query')
    res = handle_query.handle_query(raw_query.lower())
    template = loader.get_template('result.html')
    context = {
        'all_query': res,
        'query': raw_query
    }
    return HttpResponse(template.render(context, request))
