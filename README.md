# hustl.io
![Landing Page](https://i.imgur.com/wxYSafV.png)


Y15 Team Project for 10120
hustl.io is a competitive paper-trading website built for those who don't want to lose their life savings.

- Create a portfolio and invest in real stocks, just with fake money
- Add friends and create a league to start with a custom balance
- Check the leaderboards to see how well you've done

## Personal Notes
The commit history / authors can be misleading; we extensively used Live Share in the back end which is inconsistent in showing who has actually worked on the commit, leading to it showing only one person and not two. The majority of backend commits are actually co-authored by myself and [lambeau288](https://github.com/lambeau288).

### What did I contribute?
I played a role both in front and back end, contributing core parts of the following systems:
- Front end
    - Trading section
    - Your Portfolio page
    - Landing page
    - Various fixes to the overall site
- Back end
    - Trading history storage & retrieval, including managing & migrating to the live Postgres DB
    - Leagues system implementation
    - Deployment and management of live server via Heroku

### What did I learn?
My knowledge of Django has drastically improved due to this project. I have also gained a lot more experience working with databases, and have finally achieved the goal of panicking after messing up a live production database (I fixed it in the end).

### What did I enjoy?
Being able to interact with live stock market data and build a platform around it that is both engaging and almost addictive is very satisfying. I remember when the initial trading system was implemented, myself and fellow teammates couldn't put it down for the rest of the day as it was genuinely interesting and fun to test out trading strategies and compete with each other.


## Running the Server
Before running, you need to generate a (free) Finnhub API key and insert it [here](https://github.com/TorinFelton/hustl.io/blob/0ec1e2db9ab92d9372dc3b2f12be25bd46e04372/src/stock_updater.py#L32)

#### With Docker
- Go into src/ and use the "docker-compose build" command to build the docker images and "docker-compose up" to run the container.
### Without Docker
- Install requirements.txt
- Go into src/ and run "python manage.py runserver"

### Layout
- src/
    - assets/ - All CSS, JS, IMG files
    - hustlio/ - The parent django app folder
        - settings.py is only significant file in here
    - main/ - The main django app folder, where all our important py files are
    - templates/ - The folder of all our HTML templates


### Points to note
- main/urls.py is where ALL our URL requests are redirected to view functions
- XXX_views.py are files containing view functions to handle requests and respond with a template + data
- This is the LOCAL version; it is running SQLite3 (no setup required) and has TEST data for prices, etc. This is why the historical data is irregular. 
- The price updates every 5 minutes, but the graphs change only at 00:00.


See LIVE version with LIVE data: XXXXXX (Removed temporarily).
