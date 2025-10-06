# price-tracker
Python tool for scraping urls and tracking price changes, notifying the user when the price is right.

The application is deployed to [Heroku](https://www.heroku.com/) and is runned every day with Heroku Scheduler addon. When the price for some of the items falls down below the set treshold, i am notified via email for the new price of the item.
