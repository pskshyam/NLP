from pymongo import MongoClient
import pandas as pd
import numpy as np
from services.api.common.logger import set_up_logging
from services.api.util.config.cms_config import CMSConfig
from nltk.corpus import stopwords
import json

logger = set_up_logging(__name__)

class MongoDocLink:

    def _connect_mongo(self, host, port, username, password, db):
        """ A util for making a connection to mongo """
        if username and password:
            mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, 'admin')
            conn = MongoClient(mongo_uri)
        else:
            conn = MongoClient(host, port)
        return conn[db]

    #reading data from MongoDB
    def read_mongo(self,db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
        """ Read from Mongo and Store into DataFrame """
        # Connect to MongoDB
        db = self._connect_mongo(host=host, port=port, username=username, password=password, db=db)
        # Make a query to the specific DB and Collection
        cursor = db[collection].find(query)
        # Expand the cursor and construct the DataFrame
        df =  pd.DataFrame(list(cursor))
        # Delete the _id
        if no_id:
            del df['_id']
        return df
    #########

    def lookup_table_MSASOW(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here **************************')
        msaout = []
        sowout = []
        list1_fp = value['firstParty'].split(" ")
        list1_sp = value['secondParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["msaDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})
        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def lookup_table_MSASOW2(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here MSASOW2 **************************')
        msaout = []
        sowout = []
        list1_fp = value['secondParty'].split(" ")
        list1_sp = value['firstParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["msaDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})
        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def lookup_table_MSAAddendum(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here **************************')
        sowout = []
        list1_fp = value['firstParty'].split(" ")
        list1_sp = value['secondParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["msaDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})

        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def lookup_table_MSAAddendum2(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here **************************')
        sowout = []
        list1_fp = value['secondParty'].split(" ")
        list1_sp = value['firstParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["msaDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})

        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def lookup_table_SOWAddendum(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here **************************')
        sowout = []
        list1_fp = value['firstParty'].split(" ")
        list1_sp = value['secondParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["sowDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})
        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def lookup_table_SOWAddendum2(self, value, df1):
        """
        :param value: value to find the dataframe
        :param df: dataframe which constains the lookup table
        :return:
            A String representing a the data found
        """
        # Variable Initialization for non found entry in list
        print('********************* Started here **************************')
        sowout = []
        list1_fp = value['firstParty'].split(" ")
        list1_sp = value['secondParty'].split(" ")
        list1_effdt = value['effectiveDate'].split(" ")
        # for MSA and SOW linking
        for index, row in df1.iterrows():
            list2_fp = row["firstParty"].split(" ")
            list2_sp = row["secondParty"].split(" ")
            list2_effdt = [row["sowDate"]]
            print('list1_values:->', list1_fp, list1_sp, list1_effdt, value['uniqueId'])
            print('list2_values:->', list2_fp, list2_sp, list2_effdt, row['uniqueId'])
            tlistfp = list(set(list1_fp) & set(list2_fp))
            tlistsp = list(set(list1_sp) & set(list2_sp))
            tlisteffdt = list(set(list1_effdt) & set(list2_effdt))
            print('len:-', len(tlistfp), len(tlistsp), len(tlisteffdt))
            if len(tlistfp) > 0 and len(tlistsp) > 0 and len(tlisteffdt) > 0:
                sowout.append({'uniqueId': row['uniqueId'], 'category': row['category']})
        if len(sowout) > 0:
            return [value['uniqueId'], value['category'], sowout]
        else:
            return [np.nan, np.nan, np.nan]

    def preprocessdf(self, df):
        df['firstParty'] = df['firstParty'].str.lower()
        df['secondParty'] = df['secondParty'].str.lower()

        default_stopwords = set(stopwords.words('english'))
        otherEnglish = ['llp.', 'lp.', 'ltd.', 'inc.', 'pvt.', 'limited.', 'llc.', 'lc.', 'limited.', 'ltd', 'inc',
                        'pvt', 'limited', 'llc', 'lc', 'technologies', 'technology', 'solution', 'solutions', 'llp',
                        'lp', 'service', 'services', 'international', 'a', 'of', 'at', 'for', 'is', 'this', 'that',
                        'is']
        default_stopwords = default_stopwords.union(otherEnglish)
        punc = [',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', "%"]
        default_stopwords = default_stopwords.union(punc)
        df['firstParty'] = df['firstParty'].apply(
            lambda x: ' '.join([word for word in str(x).split() if word not in (default_stopwords)]))
        df['secondParty'] = df['secondParty'].apply(
            lambda x: ' '.join([word for word in str(x).split() if word not in (default_stopwords)]))
        df['firstParty'] = df['firstParty'].str.replace(',', '')
        df['secondPaself, rty'] = df['secondParty'].str.replace(',', '')
        return df

    def write_df_to_mongoDB(self, my_df, database_name, collection_name, username, password, server, mongodb_port=27017, chunk_zie=100):
        db = self._connect_mongo(host=server, port=mongodb_port, username=username, password=password, db=database_name)
        #client = MongoClient(server, int(mongodb_port))
        #db = client[database_name]
        collection = db[collection_name]
        # To write
        #collection.delete_many({})  # Destroy the collection
        collection.insert_many(my_df.to_dict('records'))
        print('MongoDB Saving Completed')
        return

    def link_process(self,host,port,username,password, session):

        ###########################Connection details###########################
        '''
        parser = ConfigParser()
        parser.read('database.config')
        username = urllib.parse.quote_plus(parser.get('database_config', 'username'))
        password = urllib.parse.quote_plus(parser.get('database_config', 'password'))
        host = parser.get('database_config', 'host')
        port = parser.get('database_config', 'port')
        srcdbase = parser.get('database_config', 'srcdb')
        dstdbase = parser.get('database_config', 'dstdb')
        srccollection = parser.get('database_config', 'srccollection')
        dstcollection = parser.get('database_config', 'dstcollection')

        print(parser.get('database_config', 'host'))
        '''

        srcdbase = CMSConfig.dbname
        srccollection = 'DocumentDetails'
        dstcollection = 'DocLinks'

        ##################### New code starts here################
        #(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True)
        mongoDF = self.read_mongo(db=srcdbase, collection=srccollection, host=host, port=port, username=username, password=password)
        mongoDF = mongoDF[mongoDF['sessionId'] == session]
        mongoDF = mongoDF[mongoDF['category'].isin(['MSA','SOW','ADDENDUM'])]
        mongoDF = mongoDF.reset_index(drop=True)
        #print(list(mongoDF['details']))
        #mongoAllDF = pd.concat([mongoDF, pd.DataFrame(list(mongoDF['details']))], axis=1).drop('details', 1)
        #mongoAllDF.to_csv('mongoALLDF.csv')

        #new code added to handle issue in sub records
        text = "{'contract':'','duration':'','effectiveDate':'','endDate':'','firstParty':'','indemnification':'','msaDate':'','payment':'','rebateInfoAvailable':'','rebate_info':'','secondParty':'','services':''}"
        mongoDF['details'] = mongoDF['details'].replace(np.nan, text, regex=True)
        mongoDF['details'] = mongoDF['details'].apply(lambda x: str(x))
        mongoDF['details'] = mongoDF['details'].map(lambda x: dict(eval(x)))
        mongoDetailsDF = mongoDF['details'].apply(pd.Series)
        print('-----------mongoDetailsDF after cleansing long text-----------')
        print(mongoDetailsDF)

        mongoDetailsDF.to_csv('mongoDetailsDF.csv', index=False)
        mongoAllDF = pd.concat([mongoDF, mongoDetailsDF], axis=1).drop('details', 1)
        print('---------mongoAllDF.columns  after processing --------------')
        print(mongoAllDF.columns)

        MSADF = mongoAllDF[mongoAllDF['category'] == 'MSA'].copy()
        SOWDF = mongoAllDF.where(mongoAllDF['category'] == 'SOW').copy()
        ADDF = mongoAllDF.where(mongoAllDF['category'] == 'ADDENDUM').copy()

        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']).issubset(SOWDF.columns)):
            SOWDF = SOWDF.dropna(subset=['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate','msaDate'])
            SOWDF = SOWDF[['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']].copy()
            SOWDF.reset_index()

        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)):
            MSADF = MSADF.dropna(subset=['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate'])
            MSADF = MSADF[['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']].copy()
            MSADF.reset_index()

        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'msaDate']).issubset(ADDF.columns)):
            ADDFMSA = ADDF.dropna(subset=['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'msaDate'])
            ADDFMSA = ADDFMSA[['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'msaDate']].copy()
            ADDFMSA.reset_index()

        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']).issubset(SOWDF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'sowDate']).issubset(ADDF.columns)):
            ADDFSOW = ADDF.dropna(subset=['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'sowDate'])
            ADDFSOW = ADDFSOW[['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'sowDate']].copy()
            ADDFSOW.reset_index()

        print('####################################################')
        print('1. completed the rows loading into DF')
        print('######### MSASOW ###################################')

        # MSA SOW linking
        print('------------------------MSA SOW ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']).issubset(SOWDF.columns)):
            if len(MSADF) > 0 and len(SOWDF) > 0:
                finMSASOW = MSADF.apply(lambda x: self.lookup_table_MSASOW(x, SOWDF.apply(lambda y: y, axis=1)), axis=1)
                finMSASOW = finMSASOW.apply(pd.Series)
                finMSASOW.columns = ['uniqueId', 'category', 'child']
                finMSASOW.replace('', np.nan, inplace=True)
                finMSASOW.dropna(inplace=True)
                print('-----------------finMSASOW-----------------')
                print(finMSASOW)
                finMSASOW.to_csv('finMSASOW.csv', index=False)
            else:
                print('No linking between MSA and SOW')
                finMSASOW = pd.DataFrame()
        else:
            print(' MSA/SOW - All columns are not present')
            finMSASOW = pd.DataFrame()

        # MSA SOW linking2
        print('------------------------MSA SOW2 ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate','msaDate']).issubset(SOWDF.columns)):
            if len(MSADF) > 0 and len(SOWDF) > 0:
                finMSASOW2 = MSADF.apply(lambda x: self.lookup_table_MSASOW2(x, SOWDF.apply(lambda y: y, axis=1)), axis=1)
                finMSASOW2 = finMSASOW2.apply(pd.Series)
                finMSASOW2.columns = ['uniqueId', 'category', 'child']
                finMSASOW2.replace('', np.nan, inplace=True)
                finMSASOW2.dropna(inplace=True)
                print('-----------------finMSASOW2-----------------')
                print(finMSASOW2)
                finMSASOW2.to_csv('finMSASOW2.csv', index=False)
            else:
                print('No linking between MSA and SOW2')
                finMSASOW2 = pd.DataFrame()
        else:
            print(' MSA/SOW - All columns are not present')
            finMSASOW2 = pd.DataFrame()

        # MSA Addendum linking
        print('------------------------MSA ADDENDUM ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'msaDate']).issubset(ADDF.columns)):


            if len(MSADF) > 0 and len(ADDFMSA) > 0:
                finMSAADD = MSADF.apply(lambda x: self.lookup_table_MSAAddendum(x, ADDFMSA.apply(lambda y: y, axis=1)), axis=1)
                print('------------MSAADD------------')
                print(finMSAADD)
                finMSAADD = finMSAADD.apply(pd.Series)
                finMSAADD.columns = ['uniqueId', 'category', 'child']
                finMSAADD.replace('', np.nan, inplace=True)
                finMSAADD.dropna(inplace=True)
                finMSAADD.to_csv('finMSAADD.csv', index=False)
            else:
                print('No linking between MSA and Addendum')
                finMSAADD = pd.DataFrame()
        else:
            print(' MSA/Addendum - All columns are not present')
            finMSAADD = pd.DataFrame()

        # MSA Addendum linking2
        print('------------------------MSA ADDENDUM2 ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate']).issubset(MSADF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'msaDate']).issubset(ADDF.columns)):
            if len(MSADF) > 0 and len(ADDFMSA) > 0:
                finMSAADD2 = MSADF.apply(lambda x: self.lookup_table_MSAAddendum2(x, ADDFMSA.apply(lambda y: y, axis=1)), axis=1)
                print('------------MSAADD2------------')
                print(finMSAADD2)
                finMSAADD2 = finMSAADD2.apply(pd.Series)
                print(len(finMSAADD2))
                finMSAADD2.replace('', np.nan, inplace=True)
                finMSAADD2.dropna(inplace=True)
                finMSAADD2.columns = ['uniqueId', 'category', 'child']
                finMSAADD2.to_csv('finMSAADD2.csv', index=False)
            else:
                print('No linking between MSA and Addendum2')
                finMSAADD2 = pd.DataFrame()
        else:
            print(' MSA/Addendum - All columns are not present')
            finMSAADD2 = pd.DataFrame()

        # SOW Addendum linking
        print('------------------------SOW ADDENDUM ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']).issubset(SOWDF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'sowDate']).issubset(ADDF.columns)):
            if len(SOWDF) > 0 and len(ADDFSOW) > 0:
                finSOWADD = SOWDF.apply(lambda x: self.lookup_table_SOWAddendum(x, ADDFSOW.apply(lambda y: y, axis=1)), axis=1)
                finSOWADD = finSOWADD.apply(pd.Series)
                finSOWADD.columns = ['uniqueId', 'category', 'child']
                finSOWADD.replace('', np.nan, inplace=True)
                finSOWADD.dropna(inplace=True)
                print(finSOWADD)
                finSOWADD.to_csv('finSOWADD.csv', index=False)
                print('len(finSOWADD) > 0-', len(finSOWADD))
            else:
                print('No linking between SOW and Addendum')
                finSOWADD = pd.DataFrame()
        else:
            print(' SOW/Addendum - All columns are not present')
            finSOWADD = pd.DataFrame()

        # SOW Addendum linking2
        print('------------------------SOW ADDENDUM2 ------------------------------')
        if (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'effectiveDate', 'msaDate']).issubset(SOWDF.columns)) and\
            (set(['firstParty', 'secondParty', 'sessionId', 'uniqueId', 'category', 'sowDate']).issubset(ADDF.columns)):
            if len(SOWDF) > 0 and len(ADDFSOW) > 0:
                finSOWADD2 = SOWDF.apply(lambda x: self.lookup_table_SOWAddendum2(x, ADDFSOW.apply(lambda y: y, axis=1)), axis=1)
                finSOWADD2 = finSOWADD2.apply(pd.Series)
                finSOWADD2.columns = ['uniqueId', 'category', 'child']
                finSOWADD2.replace('', np.nan, inplace=True)
                finSOWADD2.dropna(inplace=True)
                print(finSOWADD2)
                finSOWADD2.to_csv('finSOWADD.csv', index=False)
            else:
                print('No linking between SOW and Addendum')
                finSOWADD2 = pd.DataFrame()
        else:
            print(' SOW/Addendum - All columns are not present')
            finSOWADD2 = pd.DataFrame()

        # merge all DFs
        finalDF = pd.concat([finMSASOW,finMSASOW2,finMSAADD,finMSAADD2,finSOWADD,finSOWADD2], ignore_index=True)
        finalDF['sessionId'] = session
        finalDF['child'] = finalDF['child'].apply(lambda x: json.dumps(x))
        #finalDF = pd.concat([finMSASOW, finMSAADD, finSOWADD], ignore_index=True)
        print('----- finalDF --------------')
        print(finalDF)
        print('----- finalDF completed --------------')

        if len(finalDF) > 0:
            finalDF.to_csv('final.csv',index = False)
            self.write_df_to_mongoDB(finalDF, srcdbase, dstcollection, username, password, host, port)
        else:
            print("Empty dataframe so skipped saving to mongodb")
