# InterfaceLIFTDownloader
A python application to download the entire library of InterfaceLIFT.com for the resolutions it supports.

The application uses Python 3.9, tkinter for the GUI, and BeautifulSoup4 was used to scrape the pages for all the initial necessary data.  

## How To Use
You are free to compile the application on your own with the files in this repo, but I have also added an executable for anyone that just wants to run it quickly.

To compile navigate to the project directly and run the following command.

`pyinstaller --onefile --add-data="res_list.txt;." --add-data="wallpaper_links_without_res.txt;." --name InterfaceLIFTDownloader --noconsole main.py`

(Install pyinstaller `pip install pyinstaller` beforehand if not already installed.)

Note: The application automatically detects all resolutions on the connected monitors and selects them for downloading. If there are any other resolutions that you would like to download for selected them from the drop down list and click the add button.

When all the resolutions you require are added to the list, press start, and the wallpapers will begin to download.

There is currently a limit of 3 resolutions per run to prevent any type of ip restrictions or bans from the site.
There are currently 3924 wallpapers published on the site, with varying amounts of resolutions available for each one. Currently, for all resolutions there will be an attempt to download each wallpaper (I plan on adding blacklists for each resolution to reduce bandwidth and runtime).

Currently, the statistics for these popular screen resolutions are:

720p - 2782 wallpapers, 2,156,455,510 bytes (2GB)

1080p - 2764 wallpapers, 4,395,560,751 bytes (4.09GB)

1440p - 2289 wallpapers, 6,589,693,875 bytes (6.13GB) 

Download time and runtime will vary depending on your machine and internet connection speeds.

## Why did I make this?
For the past few years I have almost exclusively used InterfaceLIFT for my wallpapers on all my devices, but there have been some times when the site has been down.

So recently after I built my new PC I went to InterfaceLIFT to download some wallpapers and got the idea for the projects because I wanted to download all the wallpapers. 

But, I quickly realized it would take ages to download the entire library, so I decided to make this to do it for me (this took more time to make than downloading them manually but hopefully whoever uses this saves some time).

## Troubleshooting
If the executable fails to open you may need to update or install [Visual C++ Redistributable](https://support.microsoft.com/en-us/topic/the-latest-supported-visual-c-downloads-2647da03-1eea-4433-9aff-95f26a218cc0)

## Contact
Please feel free to contact me if there are any issues or concerns with the application.
steve.statia@gmail.com