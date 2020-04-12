import pymongo
from pymongo import MongoClient
import datetime
import pandas as pd
import numpy as np
import gc
gc.enable()


client_1 = MongoClient('45.122.223.198:27017',             #IP address of database
                    username = 'kapiReadOnly', #Username
                    password = 'pl2oieAt9#tnWV!Yc0',         #Password
                    authSource = 'kapi',                   #name of database
                    authMechanism = 'SCRAM-SHA-1'
                    )
database_1 = client_1['kapi']


def int_fun(post_id):
    cluster1 = database_1['reactions'].find({'fid': {'$in': post_id}},
                                            {'_id': 0, 'fid': 1, 'from_user_id': 1})
    cluster2 = database_1['comments'].find({'post_id': {'$in': post_id}},
                                           {'_id': 0, 'post_id': 1, 'from_raw_user': 1, 'from_user': 1})
    cluster3 = database_1['posts'].find({'parent_id': {'$in': post_id}},
                                        {'_id': 0, 'parent_id': 1, 'from_user': 1, 'comments_count': 1,
                                         'likes_count': 1})

    tb1 = pd.DataFrame(list(cluster1))
    # tb1 = pd.DataFrame()
    # for a in cluster1:
    #     tmp = pd.DataFrame([a])
    #     tb1 = tb1.append(tmp, ignore_index=True)

    tb2 = pd.DataFrame(list(cluster2))
    # tb2 = pd.DataFrame()
    # for b in cluster2:
    #     tmp = pd.DataFrame([b])
    #     tb2 = tb2.append(tmp, ignore_index=True)

    tb3 = pd.DataFrame(list(cluster3))
    # tb3 = pd.DataFrame()
    # for c in cluster3:
    #     tmp = pd.DataFrame([c])
    #     tb3 = tb3.append(tmp, ignore_index=True)

    for i in range(len(tb2)):
        if tb2.from_user[i] == '':
            tb2.from_user[i] = tb2.from_raw_user[i]

    gc.collect()

    return tb1, tb2, tb3


def info_fun(fid_list):
    cluster = database_1['posts'].find({'fid': {'$in': fid_list}},
                                       {'_id': 0, 'fid': 1, 'to_user': 1, 'created_date': 1,
                                        'comments_count': 1, 'shares_count': 1, 'likes_count': 1})

    info_tb = pd.DataFrame()
    for i in cluster:
        tmp = pd.DataFrame([i])
        info_tb = info_tb.append(tmp, ignore_index=True)

    gc.collect()

    return info_tb


def retrieve_fun(id_list, start_date, end_date, speed):
    tab1 = database_1['posts'].find({'to_user': {'$in': id_list},
                                     'created_date': {'$gte': start_date, '$lt': end_date},
                                     }, {
                                        '_id': 0, 'fid': 1
                                    })

    ipt = pd.DataFrame()
    for i in tab1:
        tmp = pd.DataFrame([i])
        ipt = ipt.append(tmp, ignore_index=True)

    print("There are {:} messages for processing .".format(len(ipt)))

    int_tmp = pd.DataFrame()
    cmt_tmp_tb = pd.DataFrame()
    shr_tmp_tb = pd.DataFrame()
    len_tmp = (len(ipt) // speed + 1)

    try:
        for i in range(len_tmp):
            print('==Processing to==> {:.4}%'.format(((i + 1) * 100) / len_tmp))
            tb1_tmp, tb2_tmp, tb3_tmp = int_fun(ipt['fid'][i * speed:(i + 1) * speed].tolist())
            int_tmp = int_tmp.append(tb1_tmp, ignore_index=True)
            cmt_tmp_tb = cmt_tmp_tb.append(tb2_tmp, ignore_index=True)
            shr_tmp_tb = shr_tmp_tb.append(tb3_tmp, ignore_index=True)
    except pymongo.errors.CursorNotFound:
        print("Lost cursor. Retry with skip")

    cmt_tmp = pd.DataFrame({'fid': cmt_tmp_tb.post_id, 'from_user_id': cmt_tmp_tb.from_user})
    shr_tmp = pd.DataFrame({'fid': shr_tmp_tb.parent_id, 'from_user_id': shr_tmp_tb.from_user})

    shr_tmp_tb['sub score'] = shr_tmp_tb['comments_count'] + shr_tmp_tb['likes_count']
    af_tmp = shr_tmp_tb.groupby('parent_id').agg({'sub score': 'sum'}).reset_index()
    af_tmp.columns = ['fid', 'sub score']

    total_int_tmp = int_tmp.append([cmt_tmp, shr_tmp]).drop_duplicates().reset_index(drop=True)
    total_int_tmp = total_int_tmp.groupby('fid').agg('count')
    total_int_tmp = af_tmp.set_index('fid').join(total_int_tmp, how='right')

    post_query_tmp = info_fun(total_int_tmp.index.tolist())
    post_query_tmp = post_query_tmp.set_index('fid')

    combine_tb = total_int_tmp.join(post_query_tmp)
    combine_tb['AF score'] = [np.nansum([x, y]) for x, y in
                              zip(combine_tb['from_user_id'], combine_tb['sub score'])];

    #gc.collect()

    return combine_tb


a_list = ['/lynhxynh054/',
'/uyen\.tran\.186/',
'/tuyetminh\.u/',
'/phuong\.kim\.146/',
'/thuong\.bui\.739/',
'/thinh\.caohuu/',
'/yun\.he\.391/',
'/chau\.tuyet\.37/',
'/khabichquynh/',
'/NguyenBaoLoc796/',
'/VyThuyNguyen76/',
'/minhhuong\.nguyen\.902/',
'/trang\.ipumim/',
'/hoaithu\.mc/',
'/LeuPhuongAnh\.Idol/',
'/rachel\.pham/',
'/quynh\.scarlett/',
'/ngoc\.tram\.77/',
'/kusin\.nguyen/',
'/trang\.hoxe/',
'/gaothet/',
'/trangmnguyen132/',
'/ngoclan\.nguyen/',
'/pdthiendi/',
'/quynguyen\.94801/',
'/loanhoang2212/',
'/hoatuyet109/',
'/hothanhtra91/',
'/thanhphuong\.274/',
'/sam\.nguyenphu/',
'/nghesythanhthuy/',
'/jumyphuonganh92/',
'/thanh\.chunghuyen/',
'100001319768989',
'/huyentrangbathoi/',
'/NguyenThiHongPhuong\.MeKiwi/',
'/anhnguyen\.nutrition/',
'/hienhoangxgeneducation/',
'/MinhNgoc/',
'/chef\.hoangcuong/',
'/ly\.gondola/',
'100004616538619',
'/sara\.nguyen\.543/',
'/mixuu\.mixuu\.9/',
'/hoaarum\.hoaarum/',
'/pham\.phuong\.391/',
'100009007042737',
'/bopcom/',
'/Linhnhi8/',
'/phuongloan\.pham\.31/',
'/sara\.nguyen\.543/',
'100004476107852',
'/emla\.mun/',
'/ami\.kool\.9/',
'/xu\.xixon\.1420/',
'/hoa\.my\.184/',
'/Ngoctrang1798/',
'/lockutiwa/',
'/dao\.linh\.7543/',
'100016550867197',
'/phuongnhi\.bui\.1401933/',
'100017225435318',
'/thao1988/',
'/xuantruc\.lehoang\.98/',
'/xuan\.chipbong/',
'/sinhvien\.guongmau\.7/',
'100011597771399',
'/vy\.yubin98/',
'100010190191043',
'/lula\.bongbong/',
'/pooka\.pe/',
'/trang\.nguyenthuytrang\.98/',
'/vy\.yubin98/',
'/thutra\.tran\.33/',
'100034175468993',
'/lethuy\.phamthi\.5/',
'/phuongthaohoang\.mayqueen/',
'/pandalovecoffee511/',
'/phuocsuong\.pham/',
'/whiteluxipheboy\.hoang/',
'100031837786094',
'100005447927628',
'/hang\.angel\.526/',
'100032402745316',
'/hang\.truc\.1694/',
'100009093167114',
'100004810052025',
'/honghuong\.hoanghon/',
'/trang\.ta\.39/',
'/van\.bong\.509/',
'/hothanhtra91/',
'/ny\.zenny/',
'/huyenthao\.bacsi/',
'/fi\.nguyen\.9/',
'/hatrinh\.ha95/',
'/rain\.nguyen\.338/',
'100003645240359',
'/trang\.pe\.58/',
'/tuvi\.le/',
'/thanhtu123all/',
'/nguyenngan\.allsuper/',
'/lamquyhang83/',
'/ngochuyencgn84/',
'/cobengocghech\.311/',
'/Hakhanh\.summer/',
'/harleyngocvo/',
'/heo\.coi\.98871/',
'/beminhshop/',
'/gdkhanhan/',
'100022018483880',
'/jinny\.nguyen\.7583/',
'/loan\.ho\.3/',
'/tham\.vo\.311493/',
'/sam\.ngocanh\.3/',
'/lien\.ho\.75098/',
'/thoantrangthoantrang/',
'/linh\.mum96/',
'/Vo\.t\.quynhnhu/',
'/phuongkatykaty/',
'/nhtmxxx123/',
'/nnhungle/',
'/deezay\.beheo/',
'/ieu\.luc/',
'/vjtxjx0n/',
'/trinh\.miiu/',
'/xoan\.hong\.37/',
'/Hue\.AE1/',
'/ngochoabg91/',
'/duong\.mini\.3/',
'/linh\.shin\.927/',
'100008454426355',
'100012864220207',
'/thao\.leiko/',
'/khanhloan\.tran\.5/',
'100027603482286',
'/quynh\.ngoc\.1257604/',
'/virgo\.phuongthao91/',
'/ngoc\.bong\.161/',
'/ho\.thuy\.18659/',
'/le\.hau\.3785373/',
'/Haohao1989/',
'100004589469292',
'/lananh\.nguyen\.144734/',
'100011100009173',
'/suabimvnNguyenChiThanh/',
'/le\.nguyet\.96/',
'/kimoanh29061994/',
'/na\.bon\.5686/',
'/phuoc\.vy\.2005/',
'/chipbum\.phan\.9/',
'/lehang\.nguyen\.355/',
'100011545749560',
'100012797838767',
'/hanh\.depzai\.7/',
'100016746524325',
'/tung\.ngoc\.925602/',
'/be\.nu\.1238/',
'/minh\.nguyet\.522/',
'/le\.hoang\.796/',
'100003801184541',
'100004869977585',
'/ha\.dau\.92/',
'/nguyet\.giap\.3/',
'/letranthienthanh981124/',
'/loan\.luu\.334839/',
'/huong\.giang\.50/',
'/nguyenphambaotien/',
'/hoangyen\.le\.3348/',
'/dolly\.pham\.2608/',
'/PhuongVy\.Idol/',
'/to\.ajino/',
'/rena\.nguyen\.1/',
'/tohongvan0210/',
'/thichuc\.truong/',
'/anhnguyen\.nutrition/',
'/minacosmetic92/',
'/nguyentnhung5686/',
'/nguyen\.ngoc\.ha00/',
'100004204003813']



b_list = ["100001997853167", "100003714391961", "567112096", "100004095850481", "100003798186002", "100001961447372", "100003597533936",
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
          "100003829944769", "100031837786094", "100005447927628", "100005945013345", "100032402745316", "100024180949652"]

c_list = ["100009093167114", "100004810052025", "100002944413188", "100001723596967", "100003821394311", "100007016911108",
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


gc.collect()

start_date = datetime.datetime(2018,7,1) #Year, Month, Day of start date
end_date = datetime.datetime(2018,12,31)  #Year, Month, Day of end date


r_tb = retrieve_fun(c_list, start_date, end_date, speed=10)


r_tb.to_csv('c_list.csv')
