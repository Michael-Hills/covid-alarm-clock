from main import get_covid_data

test_data = {'casesDate': '2020-12-01',
'areaName':'Exeter',
'newCases': '25',
'deathsDate':'2020-11-30',
'newDeaths':'0'}

def test_functionality():
    assert (get_covid_data(test_data)) == {'title':'Latest Covid-19 Data','content':'The last' +
    ' reported daily cases in Exeter was 25, reported on 2020-12-01. The last reported deaths' +
    ' was 0, reported on 2020-11-30. This puts Exeter in Threshold 1'}
