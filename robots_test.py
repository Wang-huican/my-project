import requests
import csv
from lxml import html

#常量

MOVIE_LIST_FILE = "csv_data/movie_list.csv"
TMDB_BASE_URL = "https://www.themoviedb.org"
TMDB_TOP_URL_1 = "https://www.themoviedb.org/movie/top-rated"#高分电影(第一页)
TMDB_TOP_URL_2 = "https://www.themoviedb.org/discover/movie/items"


#获取电影详情
def get_movie_info(movie_info_url):
    #1.发型请求， 获取电影详细数据
    movie_response = requests.get(movie_info_url, timeout=60)
    print(f"发送请求{movie_info_url}，获取电影详情数据...")
    #2.解析数据， 获取电影详情
    movie_document = html.fromstring(movie_response.text)

    movie_names = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/a/text()") #电影名称
    movie_years = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/h2/span/text()")#电影年份
    movie_dates = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='release']/text()")#电影上映时间
    movie_tags = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='genres']/a/text()")#类型
    movie_cost_times = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[1]/div/span[@class='runtime']/text()")#时长
    movie_scores = movie_document.xpath("//*[@id='consensus_pill']/div/div[1]/div/div/@data-percent") #评分
    movie_languages = movie_document.xpath("//*[@id='media_v4']/div/div/div[2]/div/section/div[1]/div/section[1]/p[3]/text()")#语言
    movie_directors = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[1]/p[1]/a/text()")#导演
    movie_authors = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/ol/li[2]/p[1]/a/text()")#作者
    movie_slogans = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/h3[1]/text()")#slogan
    movie_description = movie_document.xpath("//*[@id='original_header']/div[2]/section/div[3]/div/p/text()")#简介

    #3.返回电影详情
    movie_info = {
        "电影名称": movie_names[0].strip() if movie_names else "",
        "电影年份": movie_years[0].strip() if movie_years else "",
        "电影上映时间": movie_dates[0].strip() if movie_dates else "",
        "电影类型": ",".join(movie_tags) if movie_tags else "",
        "电影时长": movie_cost_times[0].strip() if movie_cost_times else "",
        "电影评分": movie_scores[0].strip() if movie_scores else "",
        "电影语言": movie_languages[0].strip() if movie_languages else "",
        "电影导演": ",".join(movie_directors) if movie_directors else "",
        "电影作者": ",".join(movie_authors) if movie_authors else "",
        "电影slogan": movie_slogans[0].strip() if movie_slogans else "",
        "电影简介": movie_description[0].strip() if movie_description else ""
    }
    return movie_info
#保存电影数据
def save_all_movies(all_movies):
    with open(MOVIE_LIST_FILE,"w",encoding="utf-8",newline="") as cvs_file:
        writer = csv.DictWriter(cvs_file,fieldnames=["电影名称","电影年份","电影上映时间","电影类型","电影时长","电影评分","电影语言","电影导演","电影作者","电影slogan","电影简介"])
        writer.writeheader()#写入表头
        writer.writerows(all_movies)

#主函数， 定义核心逻辑
def main():
    all_movies = []#保存所有电影数据
    #循环获取电影列表（第一页到第五页）
    for page_num in range(1,6):
        # 1.发送请求，获取高分电影数据
        if page_num == 1:
            response = requests.get(TMDB_TOP_URL_1, timeout=60)
        else:
            response = requests.post(TMDB_TOP_URL_2,
                                  f"air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page={page_num}&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2026-09-23&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400",
                                     timeout=60)
        print(f"发送请求, 访问第{page_num}页的数据，获取TMDB电影榜单数据...")

        # 2.解析数据， 获取电影列表
        document = html.fromstring(response.text)
        movie_list = document.xpath(f"//*[@id='page_{page_num}']/div[@class='card style_1']")

        # 3.遍历电影列表，获取电影详情
        for movie in movie_list:
            movie_urls = movie.xpath("./div/div/a/@href")
            if movie_urls:
                # 获取电影详情页面的URL
                movie_info_url = TMDB_BASE_URL + movie_urls[0]
                movie_info = get_movie_info(movie_info_url)
                all_movies.append(movie_info)
    #4.保存数据
    print("获取所有的电影详情， 保存电影数据到csv文件中...")
    save_all_movies(all_movies)



if __name__ == '__main__':
    main()