from datetime import datetime
from django.utils import timezone
from main.models import Stock, Portfolio, Holding,User,League,LeagueHolding,LeaguePortfolio
from main.generic_functions import getPortfolioValue, percentage_change



# -------- API modules --------
import finnhub
import json


def get_total_value(user_portfolio, league="global"):
    if league == "global":
        userHoldings = [holding for holding in Holding.objects.filter(owner = user_portfolio.owner)]
        portfolio_value = user_portfolio.owner.portfolio.balance
        for holding in userHoldings:
            portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
    else:
        leagueobj = League.objects.filter(name=league)[0]
        userHoldings = [holding for holding in LeagueHolding.objects.filter(owner = user_portfolio.owner, league=leagueobj)]
        portfolio_value = user_portfolio.balance
        for holding in userHoldings:
            portfolio_value += round((holding.stock_id.current_price * holding.amount),2)
    return portfolio_value

def update_stocks():
    print("[LOG] Updating Stocks")
    successfully_updated = []
    failed = []

    finnhub_client = finnhub.Client(api_key="<YOUR API KEY HERE>")
    stocknum = Stock.objects.all().count()
    for stock in Stock.objects.all():
        # get data
        ticket = stock.ticket
        newData = finnhub_client.quote(ticket)

        # Log success/fails for updates
        if (newData.get('c')): successfully_updated.append(ticket)
        else: failed.append(ticket)
        
        newPrice = newData.get('c')
        newDateTime = timezone.now()
        # set data
        stock.current_price = newPrice
        stock.current_datetime = newDateTime
        history = json.loads(stock.historical)
        if history.get('history'):
            if len(history['history']) >= 14: # Roll over oldest historical value after 14 days.
                day_date = int(history['history'][13]['oldTime'].split('-')[2].split(' ')[0])
                if int(newDateTime.today().strftime('%d')) != day_date:         
                    del history['history'][0]
                    history['history'].append({"oldTime": str(stock.current_datetime), "oldData": float(stock.current_price)})
        else:
            history['history'] = [{"oldTime": str(stock.current_datetime), "oldData": float(stock.current_price)}] # If history doesn't exist for some reason
        stock.historical = json.dumps(history) # Saved as text due to SQLite not supporting JSONField

        historical_prices = json.loads(stock.historical)['history']
        lastWeekPrice = float(historical_prices[len(historical_prices)-8]['oldData'])
        yesterdayPrice =  float(historical_prices[len(historical_prices)-2]['oldData'])
        todayPrice =  float(stock.current_price)
        stock.day_change = percentage_change(yesterdayPrice,todayPrice)
        stock.week_change = percentage_change(lastWeekPrice,todayPrice)


        if(stock.save()): successfully_updated += 1
    
    success_output = ','.join(successfully_updated)
    failed_output = ','.join(failed)
    print(f"[LOG] {len(successfully_updated)} stocks were updated: {success_output}")
    print(f"[LOG] {len(failed)} stocks failed to update: {failed_output}")

def update_user_portfolio(user_portfolio, league="global"):
    try:
        history = json.loads(user_portfolio.bal_hist)['history']
    except:
        failed.append(user_portfolio.owner.username)
        return False
    if len(history) == 7:
        # Cycle next
        day_date = int(history[-1]['oldTime'].split('-')[2].split(' ')[0]) # Split off day number from date
        if int(timezone.now().today().strftime('%d')) != day_date:
            del history[0]
            history.append({"oldTime": str(timezone.now()), "oldData": float(get_total_value(user_portfolio, league))})
    else:
        # reset
        history = []
        for i in range(7):
            history.append({"oldTime": str(timezone.now()), "oldData": float(get_total_value(user_portfolio, league))})
    user_portfolio.bal_hist = json.dumps({"history": history})
    user_portfolio.save()

    return True


def update_portfolios():
    # Update value history of all portfolios
    # Would be good to cache this if we were in production but we are not.
    print("[LOG] Updating portfolios")
    successful = []
    failed = []
    for user_portfolio in Portfolio.objects.all():
        if update_user_portfolio(user_portfolio): successful.append(user_portfolio.owner.username)
        else: 
            failed.append(user_portfolio.owner.username)

    for league_portfolio in LeaguePortfolio.objects.all():
        if update_user_portfolio(league_portfolio, league=league_portfolio.league.name): successful.append(league_portfolio.owner.username)
        else: failed.append(league_portfolio.owner.username)

    success_output = ','.join(successful)
    failed_output = ','.join(failed)
    print(f"[LOG] Successfully updated portfolios for: {success_output}")
    if len(Portfolio.objects.all())-len(successful) > 0:
        print(f"[LOG] Failed to update portfolios for: {failed_output}")
    userlist = []
    # update global rankings
    for player in User.objects.all():
        userHoldings = [holding for holding in Holding.objects.filter(owner = player)]
        totalPortValue = 0
        for holding in userHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        totalPortValue +=  player.portfolio.balance
        player.portfolio_value = totalPortValue
        userlist.append(player)
    userlist.sort(key = lambda x: x.portfolio_value)
    userlist = userlist[::-1]
    for i in range(0,len(userlist)):
        userlist[i].portfolio.leaderboard_ranking = i+1
        userlist[i].portfolio.save()
    # update league rankings
    for league in League.objects.all():
        leaguememberlist = []
        owner = league.owner
        userHoldings = [holding for holding in LeagueHolding.objects.filter(owner = owner, league = league)]
        totalPortValue = 0
        for holding in userHoldings:
            totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
        owner.lportfolio = LeaguePortfolio.objects.filter(owner = owner, league = league)[0]
        totalPortValue +=  owner.lportfolio.balance
        owner.lportfolio = totalPortValue 
        leaguememberlist.append(owner)
        for player in league.participants.all():
            userHoldings = [holding for holding in LeagueHolding.objects.filter(owner = player, league = league)]
            totalPortValue = 0
            for holding in userHoldings:
                totalPortValue += round((holding.stock_id.current_price * holding.amount),2)
            player.lportfolio = LeaguePortfolio.objects.filter(owner = player, league = league)[0]
            totalPortValue +=  player.lportfolio.balance
            player.lportfolio = totalPortValue
            leaguememberlist.append(player)
        leaguememberlist.sort(key = lambda x: x.lportfolio)
        leaguememberlist = leaguememberlist[::-1]
        for i in range(0,len(leaguememberlist)):
            portfolio = LeaguePortfolio.objects.filter(owner = leaguememberlist[i], league = league)[0]
            portfolio.rank = i+1
            portfolio.save()
def update_db():
    print("UPDATING DATABASE...")
    #update_stocks()
    update_portfolios()
