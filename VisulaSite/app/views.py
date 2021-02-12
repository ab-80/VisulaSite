from django.shortcuts import render, redirect
from django.http import HttpResponse
from bs4 import BeautifulSoup
import urllib3, re
from app import forms
from app.forms import GetTicker
from django.http import HttpRequest
from datetime import datetime


#display the index.html page
def index(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title' : 'Visula',
             'year':datetime.now().year,
        }
    )


#display the error.html page
def error(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/error.html',
        {
            'title' : 'Visula',
             'year':datetime.now().year,
        }
    )


#displays the about.html page and sends over info
def about(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title' : 'Visula',
            'title1':'About Visula',
            'message1':"Visula takes a ticker as input and then coherently return the stock's base information and statistics.",
            'message2' : "It is worth noting that Visula only takes numbers into consideration while evaluating a company.  Broader-market trends, political influences, product quality, and company management/direction are among the many factors that play a qualitative role in the value of a share price.  Visula is unable to account for such factors and investor discretion is necessary.",
            'title2' : "Legal",
            'message3' : "Visula is not responsible for any losses.  Buying a company's stock may result in partial or complete loss of capital.",
            'message4' : "All stock information is scraped from Yahoo Finance.",
            'year':datetime.now().year,
        }
    )


#the scrape function does all of the web-scraping and holds all of the
#variables that are displayed on the scrape.html page
#
#the Statistics, Financials, History, and Cash-Flow pages are scraped
#for certain information to be displayed
def scrape(request):
    assert isinstance(request, HttpRequest)                            


    #getting user input
    if request.method == "POST":
        tickerClass = GetTicker(request.POST)

        if tickerClass.is_valid():                  
            ticker = tickerClass.cleaned_data['ticker']


        #setting up BeautifulSoup for the key-statistics page
    try:
        url1 = ("https://finance.yahoo.com/quote/" + ticker + "/key-statistics?p=" + ticker)
        http = urllib3.PoolManager()                      
        site = http.request('GET', url1)                  
        soup = BeautifulSoup(site.data, 'html.parser')

    
        #scraping for price and extracting text
        price = soup.find('span', {"class" : "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        po = "$" + price + " per share"


        #scraping for the daily change and extracting text
        dailyChange = soup.find('span', {"class" : 'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)'})
        if dailyChange is None:
            dailyChange = soup.find('span', {"class" : 'Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($negativeColor)'})
    
        if dailyChange is None:
            dco = ""
        else:
            dco = dailyChange.text + " since trading last closed"


        #scraping for the stock name and extracting text
        stockName = soup.find('h1', {"class" : "D(ib) Fz(18px)"})
        if stockName is None:
            sn = ""
        else:
            sn = stockName.text
    except:
        return redirect('/error')

    #method to turn abbreviated number+letter into a full number
    #this method is used to find market capitalization and to find the debt+chash info
    def fullNumber(text):
        last = text[-1]
        length = len(text)
        numbers = text[0:length-1]
        float(numbers)

        if last is "T":
            output = float(numbers)*1000000000000.0
        elif last is "B":
            output = float(numbers)*1000000000.0
        elif last is "M":
            output = float(numbers)*1000000.0
        else:
            output = numbers

        return output


    #scraping for market capitalization and extracting text
    try:
        marketCap = soup.find('td', {'class' : "Ta(c) Pstart(10px) Miw(60px) Miw(80px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor)"}).text
        capAssignment = ""


        #calculating actual market cap using the fullNumber def made earlier
        totalCap = fullNumber(marketCap)


        #assigning market cap term
        if totalCap > 200000000000:
            capAssignment = "Mega Cap"
        elif totalCap > 10000000000 and totalCap <= 200000000000:
            capAssignment = "Large Cap"
        elif totalCap > 2000000000 and totalCap <= 10000000:
            capAssignment = "Mid Cap"
        else:
            capAssignment = "Small Cap"


        #this variable is what gets diplayed on the scrape.html page
        mkt_cap = capAssignment + ", with $" + marketCap + " in market capitalization"


        #getting total cash and total debt and storing them in a
        #2 element list to be diplayed in a chart
        allTables = soup.find_all('table', {'class' : "W(100%) Bdcl(c)"})
        cashDebtTable = allTables[7].find_all('tr')
        totalCash = cashDebtTable[0].find('td', {'class' : "Fw(500) Ta(end) Pstart(10px) Miw(60px)"}).text
        totalDebt = cashDebtTable[2].find('td', {'class' : "Fw(500) Ta(end) Pstart(10px) Miw(60px)"}).text

        #this variable gets displayed in scrape.html in the cash vs debt chart
        cashDebtList = [float(fullNumber(totalDebt)),float(fullNumber(totalCash))]
        list(cashDebtList)
    
    
        #opening BeautifulSoup for the financials page                               
        url2 = ("https://finance.yahoo.com/quote/" + ticker + "/financials?p=" + ticker)
        http2 = urllib3.PoolManager()                       
        site2 = http2.request('GET', url2)                  
        soup2 = BeautifulSoup(site2.data, 'html.parser')
    except:
        return redirect('/error')

    #method to extract yearly data
    def yearly(itemClass, element):
        try:
            allDivs = soup2.find_all('div', {'class' : itemClass})
            target = allDivs[element]
            output = target.find('span').text
            cleanedOutput = output.replace(",","")
            cleanedOutput = float(cleanedOutput)
            return cleanedOutput
        except:
            return redirect('/error')

    #getting last four years of gross profit

    grossProfit = []
    try:
        bar19 = yearly("Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg D(tbc)", 0)
    except:
        bar19 = 0
    try:
        bar18 = yearly("Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)", 1)
    except:
        bar18 = 0
    try:
        bar17 = yearly("Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg D(tbc)", 1)
    except:
        bar17 = 0
    try:
        bar16 = yearly("Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)", 2)
    except:
        bar16 = 0
        
    try:
        grossProfit.append(float(bar16))
        grossProfit.append(float(bar17))
        grossProfit.append(float(bar18))
        grossProfit.append(float(bar19))


        #opening BeautifulSoup for the history page                               
        url3 = ("https://finance.yahoo.com/quote/" + ticker + "/history?p=" + ticker)
        http3 = urllib3.PoolManager()                       
        site3 = http3.request('GET', url3)                  
        soup3 = BeautifulSoup(site3.data, 'html.parser')
    except:
        return redirect('/error')

    #making a function to get last 2 weeks of data
    def last2():
        fin = []
        fin = list(fin)
        table = soup3.find('table', {'class' : "W(100%) M(0)"})
        trs = table.find_all('tr')
        index = 1
        while index < 16:
            tds = []
            list(tds)
            try:
                tds = trs[index].findChildren()
            except IndexError:
                index = (index+1)
                continue
            try:
                close = tds[8].find('span').text
                closeCleaned = close.replace(",","")
                fin.append(float(closeCleaned))
                index = (index+1)
            except IndexError:
                index = (index+1)
                continue
            
        fin = list(fin)
        fin.reverse()
        return fin
        

    #use the function and assign it to a variable called threeWeeks
    twoWeeks = last2()



    #opening yahoo finance cash flow page with beautiful soup
    url4 = ("https://finance.yahoo.com/quote/" + ticker + "/cash-flow?p=" + ticker)
    http4 = urllib3.PoolManager()                       
    site4 = http4.request('GET', url4)                  
    soup4 = BeautifulSoup(site4.data, 'html.parser')

    cashFlowDiv = soup4.find('div', {'class' : "Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)"})
    cashFlowText = cashFlowDiv.find('span').text
    if cashFlowText is None:
        freeCashFlow = "Cannot locate free cash flow"
    else:
        freeCashFlow = "$" + cashFlowText + " in free cash flow"


    #the next block of code creates and executes the algorithm for the overall grade of the stock
    #it is displayed on the radar chart
    #the overallGrade list is ordered as so: [financials, growth, momentum, value]
    #everything is graded on a scale of 1-4
    overallGrade = []
    financialScore = 0
    growthScore = 0
    momentumScore = 0
    valueScore = 1
    

    #financialScore evaluator
    cash = float(fullNumber(totalCash))
    debt = float(fullNumber(totalDebt))
    if debt / cash < 1 :
        financialScore = 4
    elif debt / cash < 1.8 and debt / cash >= 1 :
        financialScore = 3
    elif debt / cash < 2.7 and debt / cash >= 1.8 :
        financialScore = 2
    else:
        financialScore = 1

    overallGrade.append(financialScore)
    


    #growthScore evaluator
    firstTwo = int(bar16) + int(bar17)
    secondTwo = int(bar18) + int(bar19)

    if firstTwo > secondTwo:
        growthScore = 1
    elif secondTwo / firstTwo > 0 and secondTwo / firstTwo <= 1.2:
        growthScore = 2
    elif secondTwo / firstTwo > 1.2 and secondTwo / firstTwo <= 1.4:
        growthScore = 3
    else:
        growthScore = 4

    overallGrade.append(growthScore)



    #momentumScore evaluator
    firstDay = twoWeeks[0]
    lastDay = twoWeeks[13]

    if lastDay < firstDay:
        momentumScore = 1
    elif lastDay / firstDay > 0 and lastDay / firstDay <= 1.05:
        momentumScore = 2
    elif lastDay / firstDay > 1.05 and lastDay / firstDay <= 1.1:
        momentumScore = 3
    else:
        momentumScore = 4

    overallGrade.append(momentumScore)


    #valueScore evaluator
    cashFlowCleaned = cashFlowText.replace(",","")
    moneyValue = cash + float(cashFlowCleaned)

    if moneyValue >= 50000000000:
        valueScore = 4
    elif moneyValue >= 20000000000 and moneyValue < 50000000000:
        valueScore = 3
    elif moneyValue >= 500000000 and moneyValue < 20000000000:
        valueScore = 2
    else:
        valueScore = 1

    overallGrade.append(valueScore)


    list(overallGrade)


        
    return render(
        request,
        'app/scrape.html', 
        {
            'title' : 'Visula',                        
            'year' : datetime.now().year,

            #for the information box
            'name' : sn,
            'price' : po,
            'daily_change' : dco,
            'marketCap' : mkt_cap,
            'cashflow' : freeCashFlow,

            #for the graphs
            'profit' : grossProfit,
            'two_weeks' : twoWeeks,
            'cash_debt' : cashDebtList,
            'overall_grade' : overallGrade,
            
        }
    )



def request_page(request):
    if(request.GET.get('mybtn')):
        views.scrape( int(request.GET.get('tickerInput')) )
    return render(request,'app/index.html')

