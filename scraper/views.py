from django.shortcuts import render
from .forms import SearchForm
from .utils import scrape_google_maps
import pandas as pd
import csv
from django.http import HttpResponse


def home(request):
    form = SearchForm()
    context = {'form': form}
    return render(request, 'home.html', context)

def results(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            try:
                data = scrape_google_maps(query)
            except Exception as e:
                return render(request, 'results.html', {'error': str(e)})

            df = pd.DataFrame(data)
            # Convert dataframe to HTML table (safe to display)
            table_html = df.to_html(classes='table table-striped', index=False)

            return render(request, 'results.html', {'table': table_html, 'query': query})
    else:
        form = SearchForm()
    return render(request, 'home.html', {'form': form})
def download_csv(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        data = []
        try:
            data = scrape_google_maps(query)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{query}_results.csv"'

        writer = csv.DictWriter(response, fieldnames=["Business Name", "Phone Number", "Address", "Website", "Email"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

        return response
    else:
        return HttpResponse("Invalid request")


