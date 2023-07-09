from dotenv import load_dotenv

from lib.NewsSentiment import DB_interaction, MarketSentiment

# load env variables
load_dotenv()

if __name__=="__main__":
    with DB_interaction() as db:
        if not db.isTodayInDB():
            print("Updating")
            ms = MarketSentiment()
            ms.addCityIndexes(db.getCityIndexesDict())
            ret = db.storeLatestSentiment(ms.getSentiment())
            print(ret)
        else:
            print("Up-to-date")