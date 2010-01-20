# C-SPAN.org plugin for plex media server

# copyright 2009 Billy Joe Poettgen
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# All images except for cspan logo are free use images from wikimedia commons


import re, string
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

CSPAN_PREFIX   = "/video/C-SPAN"
videoURL       = "http://www.c-spanarchives.org/library/includes/templates/library/flash_popup.php?pID="
frontURL       = "http://www.c-spanarchives.org/library/index.php?main_page=index"
searchDate     = "http://www.c-spanarchives.org/library/index.php?main_page=basic_search&sort=date&query="
searchURL      = "http://www.c-spanarchives.org/library/index.php?main_page=basic_search&query="
CACHE_INTERVAL = 3600


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(CSPAN_PREFIX, MainMenu, 'C-SPAN', 'icon-default.png', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'C-SPAN'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  DirectoryItem.thumb = R('icon-default.png')
  InputDirectoryItem.thumb = R('icon-default.png')
  VideoItem.thumb = R('icon-default')
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################
def MainMenu():
  dir = MediaContainer()
  
  dir.Append(Function(DirectoryItem(Live,      title="C-SPAN Channel Live Sreams",)))
  dir.Append(Function(DirectoryItem(Library,   title="C-SPAN Video Library", thumb=R('libr.jpg'))))

  dir.Append(Function(InputDirectoryItem(doSearch, title="Search CSPAN Archives",prompt='Enter search query')))
  return dir

###################################################################################################

########################### Live Feeds #######################################################
def Live(sender):
  dir = MediaContainer(title2='C-SPAN Channel Live Streams', viewGroup='Details')
  dir.Append(VideoItem('http://play.rbn.com/play.asx?url=cspan/cspan/wmlive/cspan1v.asf&amp;proto=mms?mswmext=.asx',
                  title='C-SPAN Live',
                  thumb=R('cspan1.jpg'),
                  summary="C-SPAN offers gavel to gavel coverage of the U.S. House of Representatives. C-SPAN also offers a variety of public affairs programming including congressional hearings, press briefings from the White House, State Department and Pentagon, campaign and election coverage, and international programming.",
                  ))
  dir.Append(VideoItem('http://play.rbn.com/play.asx?url=cspan/cspan/wmlive/cspan2v.asf&amp;proto=mms?mswmext=.asx',
                  title='C-SPAN 2 Live',
                  thumb=R('temp2.jpg'),
                  summary="C-SPAN 2 offers gavel to gavel coverage of the U.S. Senate. C-SPAN2 also offers a balanced variety of public affairs programming when the Senate is in adjournment, including congressional committee hearings, press briefings, newsmaker speeches & public policy discussions.",
                  ))
  dir.Append(VideoItem('http://play.rbn.com/play.asx?url=cspan/cspan/wmlive/cspan3v.asf&amp;proto=mms?mswmext=.asx',
                  title='C-SPAN 3 Live',
                  thumb=R('cspan3.jpg'),
                  summary="C-SPAN3 offers history programming and Congressional committee coverage.",
                  ))
#  dir.Append(TrackItem('http://play.rbn.com/play.asx?url=cspan/cspan/wmlive/cspan4db.asf&proto=mms',
#                  title='C-SPAN Radio Live',
#                  thumb='',
#                  art='',
#                 bandwidth=200,
#                  summary="C-SPAN Radio offers commercial-free public affairs programming 24 hours a day. You'll hear live coverage from Washington of important congressional hearings, key speeches from national leaders, along with archival recordings of presidential tapes, military memoirs & judicial proceedings from contemporary times and before the advent of television.",
#                  ))


  return dir

########################### Video Library ################################################
def Library(sender):
  dir = MediaContainer(title2='Video Library',)
  dir.Append(Function(DirectoryItem(MostWatched,  title='Most Watched Programs',)))
  dir.Append(Function(DirectoryItem(GetVids,      title='Featured Programs'), page=frontURL, path="id('featuredContent')/table/tbody/tr/td[2]/div[2]/a/@href", title2='Featured Programs'))
  dir.Append(Function(DirectoryItem(Categories,   title='Video Categories',)))
  dir.Append(Function(DirectoryItem(Series,       title='Video Series',)))
  dir.Append(Function(DirectoryItem(GetVids,      title='Obama White House', thumb=R('obama1.jpg')), page=frontURL, path="id('recentCampaign2008Content')//div/div/div[2]/a//@href", title2='Obama White House'))
  dir.Append(Function(DirectoryItem(GetVids,      title='Recent Congressional Committees', thumb=R('committee1.jpg')), page=frontURL, path="id('recentCommitteesContent')//div/div/div[2]/a//@href", title2="Recent Congressional Committees"))
  dir.Append(Function(DirectoryItem(GetVids,      title='Recent BookTV Programs', thumb=R('book1.jpg')), page=frontURL, path="id('recentBookTVContent')//div/div/div[2]/a/@href", title2="Recent BookTV"))
  return dir

###########################################

def GetPID(url):
  
  page = XML.ElementFromURL(url, isHTML=True, errors="ignore")
  PID = page.xpath('//table[@class="productVideoInfo"]//tr[1]//td[2]')[0].text
  return PID
###########################################
####################### GetVids function #################################### 
# pass in the page to parse and the xpath used (and the title2)

def GetVids(sender, title2, page, path):
  dir = MediaContainer(title2=title2, viewGroup='Details')

  #Get details page URLs
  pageXML = XML.ElementFromURL(page, isHTML=True, errors="ignore")
  detailsURL = pageXML.xpath(path)
  
  # Loop through all details page urls, get infos and video
  for y in range(len(detailsURL)):
    #load xml for details page
    detailsPage = XML.ElementFromURL(detailsURL[y], isHTML=True, errors="ignore")
    #weed out not yet available and stuff only for sale
    if detailsPage.xpath("id('streamLink')/fieldset/legend") == []:
      continue
    #get title
    title = detailsPage.xpath("id('productName')//text()")[0]
    #get thumb
    thumb = detailsPage.xpath("id('productMainImage')/a/@href")[0]
    #get summary #there's gotta be an easier way to cat the paragraphs...
    sums = detailsPage.xpath('//div[@id="productDescription"]//*')
    summary = ""
    for x in sums:
      if x.text != None:
        summary = summary + x.text
    #get info details, should Really be a better way to do this
    infos = detailsPage.xpath('//table[@class="productVideoInfo"]//tr//td')
    summary = summary + "\n"
    for x in range(len(infos)):
      if infos[x].text != None:
        if x%2 == 0:
          summary = summary + "\n%s" % infos[x].text
        else:
          summary = summary + infos[x].text
    #finally, append the actual WebVideoItem
    dir.Append(WebVideoItem(videoURL + GetPID(detailsURL[y]), title=title, thumb=thumb, summary=summary))
  #add next link to next page of results
  nextPage = pageXML.xpath("//a[@title=' Next Page ']/@href")
  if nextPage != []:
    dir.Append(Function(DirectoryItem(GetVids, title="Next 10 Results"), page=nextPage[0]+"",  path=path, title2=title2))
  #for search pages
  elif nextPage == []:
    pageNumber = pageXML.xpath("//form[@name='next']//input[@name='start']/@value")
    if pageNumber != []:
      nextPage = page + "&start=" + str(pageNumber).strip("['']")
      if nextPage != None:
        dir.Append(Function(DirectoryItem(GetVids, title="Next 10 Results"), page=nextPage,  path=path, title2=title2))
  return dir


###########################################
def MostWatched(sender):
  dir = MediaContainer(title2='Most Watched Programs')
  dir.Append(Function(DirectoryItem(GetVids, title="Last 7 days"), page=frontURL+"&sort=4d&rank_time=l7d", path="id('streamingRanksContent')/table[1]//a/@href", title2="Most Watched | 7 days"))
  dir.Append(Function(DirectoryItem(GetVids, title="Last 30 days"), page=frontURL+"&sort=4d&rank_time=l30d", path="id('streamingRanksContent')/table[1]//a/@href", title2="Most Watched | 30 days"))
  dir.Append(Function(DirectoryItem(GetVids, title="All"), page=frontURL+"&sort=4d&rank_time=at", path="id('streamingRanksContent')/table[1]//a/@href", title2="Most Watched | All"))
  return dir


def Categories(sender):
  dir = MediaContainer(title2='Video Categories',)
  dir.Append(Function(DirectoryItem(GetVids, title="American Profile"), page=frontURL+"&cPath=6_7", path="//table//td[3]//a//@href", title2="American Profile"))
  dir.Append(Function(DirectoryItem(GetVids, title="Booknotes", thumb=R('book2.jpg')), page=frontURL+"&cPath=6_8", path="//table//td[3]//a//@href", title2="Booknotes"))
  dir.Append(Function(DirectoryItem(GetVids, title="C-SPAN Special"), page=frontURL+"&cPath=6_9", path="//table//td[3]//a//@href", title2="C-SPAN Special"))
  dir.Append(Function(DirectoryItem(GetVids, title="Call-In"), page=frontURL+"&cPath=6_10", path="//table//td[3]//a//@href", title2="Call-In"))
  dir.Append(Function(DirectoryItem(GetVids, title="Congressional Committee", thumb=R('committee2.jpg')), page=frontURL+"&cPath=6_11", path="//table//td[3]//a//@href", title2="Congressional Committee"))
  dir.Append(Function(DirectoryItem(GetVids, title="Congressional Proceeding", thumb=R('proceding.jpg')), page=frontURL+"&cPath=6_12", path="//table//td[3]//a//@href", title2="Congressional Proceeding"))
  dir.Append(Function(DirectoryItem(GetVids, title="Interview"), page=frontURL+"&cPath=6_13", path="//table//td[3]//a//@href", title2="Interview"))
  dir.Append(Function(DirectoryItem(GetVids, title="National Press Club Speech"), page=frontURL+"&cPath=6_14", path="//table//td[3]//a//@href", title2="National Press Club"))
  dir.Append(Function(DirectoryItem(GetVids, title="News Conference"), page=frontURL+"&cPath=6_15", path="//table//td[3]//a//@href", title2="News Conference"))
  dir.Append(Function(DirectoryItem(GetVids, title="Public Affairs Event"), page=frontURL+"&cPath=6_16", path="//table//td[3]//a//@href", title2="Public Affairs"))
  dir.Append(Function(DirectoryItem(GetVids, title="Q&A"), page=frontURL+"&cPath=6_32", path="//table//td[3]//a//@href", title2="Q&A"))
  dir.Append(Function(DirectoryItem(GetVids, title="White House Event"), page=frontURL+"&cPath=6_17", path="//table//td[3]//a//@href", title2="White House Event"))
  return dir

def Series(sender):
  dir = MediaContainer(title2='Video Series',)
  dir.Append(Function(DirectoryItem(GetVids, title="America and the Courts"), page=frontURL+"&cPath=18_19", path="//table//td[3]//a//@href", title2="America and the Courts"))
  dir.Append(Function(DirectoryItem(GetVids, title="American Perspectives"), page=frontURL+"&cPath=18_20", path="//table//td[3]//a//@href", title2="American Perspectives"))
  dir.Append(Function(DirectoryItem(GetVids, title="American Presidents"), page=frontURL+"&cPath=18_21", path="//table//td[3]//a//@href", title2="American Presidents"))
  dir.Append(Function(DirectoryItem(GetVids, title="American Writers"), page=frontURL+"&cPath=18_22", path="//table//td[3]//a//@href", title2="American Writers"))
  dir.Append(Function(DirectoryItem(GetVids, title="BookTV"), page=frontURL+"&cPath=18_23", path="//table//td[3]//a//@href", title2="BookTV"))
  dir.Append(Function(DirectoryItem(GetVids, title="Booknotes"), page=frontURL+"&cPath=18_24", path="//table//td[3]//a//@href", title2="Booknotes"))
  dir.Append(Function(DirectoryItem(GetVids, title="Communicators"), page=frontURL+"&cPath=18_36", path="//table//td[3]//a//@href", title2="Communicators"))
  dir.Append(Function(DirectoryItem(GetVids, title="History"), page=frontURL+"&cPath=18_25", path="//table//td[3]//a//@href", title2="History"))
  dir.Append(Function(DirectoryItem(GetVids, title="Newsmakers"), page=frontURL+"&cPath=18_35", path="//table//td[3]//a//@href", title2="Newsmakers"))
  dir.Append(Function(DirectoryItem(GetVids, title="Road to the Whitehouse"), page=frontURL+"&cPath=18_28", path="//table//td[3]//a//@href", title2="Road to the Whitehouse"))
  dir.Append(Function(DirectoryItem(GetVids, title="School Bus"), page=frontURL+"&cPath=18_29", path="//table//td[3]//a//@href", title2="School Bus"))
  dir.Append(Function(DirectoryItem(GetVids, title="Tocqueville"), page=frontURL+"&cPath=18_30", path="//table//td[3]//a//@href", title2="Tocqueville"))
  dir.Append(Function(DirectoryItem(GetVids, title="Washington Journal"), page=frontURL+"&cPath=18_31", path="//table//td[3]//a//@href", title2="Washington Journal"))
  
  return dir

########################### Search Function

def doSearch(sender, query):
  dir = MediaContainer(title2="Search Results")
  queryURL = String.URLEncode(query)
  searchPage =  searchDate + queryURL
  searchPaths = "//b//a//@href"
  dir.Append(Function(DirectoryItem(GetVids, title="Search Results by Date, Newest first"), page=searchPage, path=searchPaths, title2="Search Results"))
  searchPage = searchURL + queryURL + "&sort=date&reverse=false"
  dir.Append(Function(DirectoryItem(GetVids, title="Search Results by Date, Oldest First"), page=searchPage, path=searchPaths, title2="Search Results"))
  searchPage = searchURL + queryURL
  dir.Append(Function(DirectoryItem(GetVids, title="Search Results by Relevancy"), page=searchPage, path=searchPaths, title2="Search Results"))
  
  return dir


