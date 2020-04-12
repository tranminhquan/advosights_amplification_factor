import pandas as pd
import numpy as np
import datetime
from pymongo import MongoClient
from time import time


client1 = MongoClient('45.122.223.198:27017',               #IP address of database
                    username = 'kapiReadOnly',              #Username
                    password = 'pl2oieAt9#tnWV!Yc0',        #Password
                    authSource = 'kapi',                    #name of database
                    authMechanism = 'SCRAM-SHA-1')
kapi = client1['kapi']


client = MongoClient('45.122.223.198:27017',               #IP address of database
                    username = 'kpi-v2R',                  #Username
                    password = 'EecvKJxdTQ1JEK8J2FA',      #Password
                    authSource = 'kpi-v2',                 #name of database
                    authMechanism = 'SCRAM-SHA-1')
kpitest = client['kpi-v2']


def get_ge_post(users_list, start_date, end_date):
    cluster = kapi['posts'].find({'to_user': {'$in': users_list},
                                  'parent_id': None,'created_date': {'$gte': start_date, '$lt': end_date}},
                                 {'_id': 0, 'fid': 1, 'to_user': 1, 'created_date': 1,
                                  'comments_count': 1, 'shares_count': 1, 'likes_count': 1})
    tb = pd.DataFrame(list(cluster))
    # tb = pd.DataFrame()
    # for a in cluster:
    #     tmp = pd.DataFrame([a])
    #     tb = tb.append(tmp, ignore_index=True)

    tb['total_int'] = [np.nansum([x, y, z]) for x, y, z in
                       zip(tb['comments_count'], tb['likes_count'], tb['shares_count'])]

    return tb


def get_me_post(users_list, industry, start_date, end_date):
    cluster = kpitest['posts'].find({'to_user': {'$in': users_list},
                                  'industry': industry, 'parent_id': None,
                                  'created_date': {'$gte': start_date, '$lt': end_date}},
                                 {'_id': 0, 'fid': 1, 'to_user': 1, 'created_date': 1,
                                  'comments_count': 1, 'shares_count': 1, 'likes_count': 1})

    tb = pd.DataFrame(list(cluster))
    # tb = pd.DataFrame()
    # for a in cluster:
    #     tmp = pd.DataFrame([a])
    #     tb = tb.append(tmp, ignore_index=True)

    tb['total_int'] = [np.nansum([x, y, z]) for x, y, z in
                       zip(tb['comments_count'], tb['likes_count'], tb['shares_count'])]

    return tb

user_list = ["100001997853167", "100003714391961", "567112096", "100004095850481", "100003798186002", "100001961447372", "100003597533936",
          "100005839453026", "100009887565225", "100010333095645", "100006280091794", "697906484", "1347383858", "100000201925350",
          "100001131635765", "1122706035", "1165047523", "100000258961669", "595494437", "554757389", "719335150", "100001261711300",
          "1362923905", "100002708846347", "100000718348778", "100001650992984", "100000197527970", "100007016911108", "100000322372457",
          "100008358601713", "100002114037872", "100011333061667", "100012780704777", "100001319768989", "100002674204353", "100000641426063",
          "100003713187043", "100001248952165", "698970041", "537414652", "100000543567447", "100004616538619", "100001483356457",
          "100004538941102", "100004267633521", "100000250783293", "100009007042737", "100000119596344", "100000339908814",
          "100000359650093", "100001483356457", "100004476107852", "100004242545806", "100003569823682", "100007203818622",
          "100003736677225", "100008566115322", "100004054731543", "100004093307559", "100016550867197", "100025194291968",
          "100017225435318", "100005435264199", "100027817692443", "100002628945110", "100000529669670", "100011597771399",
          "100005428203333", "100010190191043", "100008405467721", "100006207061063", "100004996991660", "100005428203333",
          "100004319018554", "100034175468993", "100003534289762", "100007417149329", "100001611307915", "100006824761488",
          "100003829944769", "100031837786094", "100005447927628", "100005945013345", "100032402745316", "100024180949652",
          "100009093167114", "100004810052025", "100002944413188", "100001723596967", "100003821394311", "100007016911108",
          "100003029547967", "100011311924354", "100000090674282", "100009175333303", "100003274585860", "100003645240359",
          "100003190063920", "100002947761648", "100009311441393", "100008544251169", "100006492785190", "100012649321912",
          "100015344626642", "100004016977149", "100003707632771", "100001594371873", "100003262562826", "100002952941432",
          "100002952941432", "100005735466796", "100002879804954", "100012799261681", "100004916611413", "100005762618701",
          "100003149305591", "100001142409674", "100005799065117", "100003931405833", "100009161337558", "100001034079001",
          "100003284551416", "100009151854812", "100000115688426", "100004095923076", "100006717690049", "100014514974681",
          "100002984603079", "100007066507552", "100006498856061", "100008454426355", "100012864220207", "100003748632824",
          "100002324898695", "100027603482286", "100010293311018", "1322622673", "100012423076999", "100007906965900",
          "100005606079315", "100003641317530", "100004589469292", "100003153315263", "100011100009173", "100015642520842",
          "100003304376505", "100009765121790", "100028448392294", "100012465906537", "100010240698725", "100003591235867",
          "100011545749560", "100012797838767", "100004334560324", "100016746524325", "100009552242711", "100006054761744",
          "100000235228067", "100003018106585", "100003801184541", "100004869977585", "100005266897640", "100003808997429",
          "100003811071955", "100011510522677", "1584345319", "100004837337817", "100000941004296", "100000761988848",
          "103592947280", "100000185051030", "726299237", "100011842266808", "100003713187043", "100002136458858",
          "100002867788185", "100006485900931", "100004204003813"]

start_date = datetime.datetime(2018,7,1)
end_date = datetime.datetime(2018,12,31)
industry = 'baby_milk_powder'
brand = 'optimum' #'apple', 'huawei', 'oppo', 'samsung' # 'nan', 'friso', 'similac', 'enfa', 'optimum'

print('start query ge')
start = time()
ge_tol = get_ge_post(user_list, start_date, end_date)
print(ge_tol.info())
print('end query ge:', time() - start)
print('='*50)
print('start query me')
start = time()
me_tol = get_me_post(user_list, industry, start_date, end_date)
print('end query me', time() - start)


cc_tol_tb = (me_tol
             .groupby(['to_user'])
             .agg({'fid': 'count'})
             .rename(columns={'fid': 'number_pst'})
             .reset_index())



def cc_fun(to_user, num_me_post):
   cc = (me_tol[me_tol.to_user == to_user ].nlargest(int(num_me_post*.1 + .9), 'total_int').total_int.mean()/
     ge_tol.nsmallest(int(ge_tol.shape[0]*.1 + .9), 'total_int').total_int.mean())*np.log10(num_me_post + 1)

   return cc

cc_tol_tb['cc score'] = cc_tol_tb.apply(lambda x: cc_fun(x['to_user'], x['number_pst']), axis=1)

cc_tol_tb = cc_tol_tb.sort_values('cc score', ascending=False)

cc_tol_tb.to_csv('cc_scr_test.csv')