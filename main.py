import requests, urllib3, os
from tkinter import *
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# The format of the url is: https://interfacelift.com/wallpaper/details/WALLPAPER_NUM/
# We need to append the wallpaper number to then end of the url with the '/' or the page will not be found
# Starts at number 3 and goes to 4201, but there are only 3924 wallpapers
# 4201-3 = 3998; 3998-3924 = 74 missing pictures in the loop
# 393 total pages
# There is a

urllib3.disable_warnings()
res_information = []
res_sizes = []
wallpaper_links = []
wallpaper_errors = []
pageUrl = "http://interfacelift.com/wallpaper/downloads/date/any/index"  # + pageNUmber + ".html"
urlSuffix = ".html"

# example wallpaper link https://interfacelift.com/wallpaper/7yz4ma1/03144_albionfalls_2560x1440.jpg
baseWallpaperUrl = "https://interfacelift.com/wallpaper/7yz4ma1/0"
res1080 = "_1920x1080.jpg"
res1440 = "_2560x1440.jpg"

os.makedirs(os.getcwd() + "/Wallpapers/1920x1080/", exist_ok=True)
os.makedirs(os.getcwd() + "/Wallpapers/2560x1440/", exist_ok=True)
path1080 = os.getcwd() + "/Wallpapers/1920x1080/"
path1440 = os.getcwd() + "/Wallpapers/2560x1440/"

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def build_image_url_without_res(image_name, image_id):
    return baseWallpaperUrl + image_id + "_" + image_name


def download_wallpaper_to_file(wallpaper_url, pictureInfo):
    # wallpaper_url = build_image_url(pictureInfo[0], pictureInfo[2])
    image_data = session.get(wallpaper_url, stream=True)
    if image_data.status_code == 200:
        if not os.path.exists(path1080 + pictureInfo[0] + ".jpg"):
            with open(path1080 + pictureInfo[0] + ".jpg", 'wb') as f:
                f.write(image_data.content)
                print("Downloaded " + pictureInfo[0] + ".jpg")
                return True
        else:
            print("Image " + pictureInfo[0] + ".jpg already exists.")
            return True
    else:
        print("Given resolution is not available for the current wallpaper: " + pictureInfo[2])
        print("Status code: " + image_data.status_code)
    return False


def scrap_pages_for_wallpaper_urls():
    for pageNum in range(1, 394):
        page_num_as_string = str(pageNum)
        new_url = pageUrl + page_num_as_string + urlSuffix

        response = session.get(new_url, verify=False)
        if not response.status_code == 200:
            wallpaper_errors.append(pageNum)
        else:
            soup = BeautifulSoup(response.text, features="lxml")
            functions = soup.find_all('select')
            for x in functions:
                onchange_func_text = x.get('onchange')
                starting_index = onchange_func_text.find("(")
                picture_info = onchange_func_text[starting_index:].replace("'", "")
                picture_info = picture_info.strip("()")
                picture_info = picture_info.split(",")
                del picture_info[1]

                wallpaper_links.append(build_image_url_without_res(picture_info[0], picture_info[1]))
            print("Page " + page_num_as_string + " complete.")


def save_wallpaper_link_to_file():
    with open("wallpaper_links_without_res.txt", 'w') as text_file:
        for index in wallpaper_links:
            text_file.write("".join(index) + "\n")


def generate_gui():
    tk = Tk()
    tk.title('InterfaceLIFT Bulk Wallpaper Downloader')

    frame = Frame(master=tk, width=500, height=500)
    frame.pack()

    yes = StringVar(tk)
    yes.set("Please select your resolution")
    res_dropdown = OptionMenu(tk, yes, *res_information)
    res_dropdown.pack()

    tk.mainloop()


def read_data_from_file():
    reader = open("res_list.txt", 'r')
    reader.readline()
    for line in reader:
        res_data = line.split(':')
        res_information.append(res_data[0])
        res_sizes.append(res_data[1])


def main():
    read_data_from_file()
    generate_gui()
    if os.path.exists("wallpaper_links_without_res.txt"):
        return True


if __name__ == '__main__':
    main()

# dat = {
#     "resolution": "1920x1080"
# }
# response = session.request()
# response = session.get(baseUrl, verify=False, params=dat).text

# soup = BeautifulSoup(response, features="lxml")
# wallpapers = soup.find_all("id=wallpaper")
# print(wallpapers)

# for x in range(0, 4202):
#     wallpaperNum = str(x)
#     newUrl = (baseUrl + wallpaperNum + "/")
#     response = session.get(newUrl, verify=False)
#     if response.status_code != 200:
#         missingTotal += 1
#         missingIDs.append(x)
#     print(newUrl + ": " + str(response.status_code))

# print(missingTotal)

# baseUrl = "http://interfacelift.com/wallpaper/details/4201/"
# pageUrlTest = "http://interfacelift.com/wallpaper/downloads/date/any/index1.html"

# response = session.get(pageUrl + "1.html", verify=False)
#     soup = BeautifulSoup(response.text, features="lxml")
#     functions = soup.find_all('option')
#
#     for x in functions:
#         text = x.text
#         value = x.get('value')
#         print(text + ':' + value)
