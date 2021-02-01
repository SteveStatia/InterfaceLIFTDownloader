import requests, urllib3, os
from tkinter import *
from tkinter.ttk import *
from time import sleep
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
selected_resolutions = []
wallpaper_errors = []
progressbar_position = 0
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
        progressbar_position = pageNum
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
    progressbar_position = 0


def save_wallpaper_link_to_file():
    with open("wallpaper_links_without_res.txt", 'w') as text_file:
        for index in wallpaper_links:
            text_file.write("".join(index) + "\n")


def gui():
    tk = Tk()
    tk.title('InterfaceLIFT Bulk Wallpaper Downloader')
    tk.geometry("400x300")
    tk.resizable(False, False)


    # Drop down resolution selection menu
    # option_menu_selection = StringVar(tk)
    # option_menu_selection.set(res_information[0])
    # res_dropdown = OptionMenu(tk, option_menu_selection, *res_information)
    # res_dropdown.pack(side=BOTTOM)

    selected_resolutions_list_box = Listbox(tk, width=40, height=10)
    selected_resolutions_list_box.grid(column=2, row=1)

    res_dropdown = Combobox(tk, state="readonly")
    res_dropdown['values'] = res_information
    res_dropdown.current(0)
    res_dropdown.grid(column=2, row=2)

    def add_res_to_list():
        if res_dropdown.get() in selected_resolutions:
            print("Resolution is already selected.")
        else:
            selected_resolutions.append(res_dropdown.get())
            selected_resolutions_list_box.insert('anchor', res_dropdown.get())
            print(selected_resolutions)

    # Button to add resolutions to the list of wallpaper downloads
    add_button = Button(master=tk, text="Add", command=add_res_to_list)
    add_button.grid(column=1, row=3)

    def remove_res_from_list():
        try:
            selected_resolutions.remove(selected_resolutions_list_box.get(selected_resolutions_list_box.curselection()))
            selected_resolutions_list_box.delete(selected_resolutions_list_box.curselection())
        except TclError:
            print("Nothing selected")

    remove_button = Button(master=tk, text="Remove", command=remove_res_from_list)
    remove_button.grid(column=3, row=3)

    def clear_list():
        selected_resolutions.clear()
        selected_resolutions_list_box.delete(0, END)

    clear_button = Button(master=tk, text="Clear List", command=clear_list)
    clear_button.grid(column=3, row=4)

    def refresh_command():
        teams = range(10)
        popup = Toplevel()
        popup.grab_set()
        Label(popup, text="Files being downloaded").grid(row=0, column=0)

        progress = 0
        progress_var = DoubleVar()
        progress_bar = Progressbar(popup, variable=progress_var, maximum=100)
        progress_bar.grid(row=1, column=0)  # .pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        popup.pack_slaves()

        progress_step = float(100.0 / len(teams))
        for team in teams:
            popup.update()
            sleep(1)  # lauch task
            progress += progress_step
            progress_var.set(progress)
        popup.destroy()

    fetch_urls_button = Button(master=tk, text="Refresh", command=refresh_command)
    fetch_urls_button.grid(column=2, row=5)

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
    gui()
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
