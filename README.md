
---
title: 'DeepNews.ai'
---
===
The objective of this project is to develop a messenger bot, which provides a technological watch on a specific theme (artificial intelligence in our case).

The project operates in several stages:

1. Load and clean the previously crawled data 
2. We get the last users and create a session for them if they are new
3. We load the data of each user and we reentrain the DNN
4. We predict which articles are the most suitable for each user
5. We update the data on S3

![Alt](UserData/Deepnews.ai.png).

# Build your own recommendation system with Facebook Messenger

The purpose of the tutorial is to give you a guideline to develop your own recommendation system. We're going to build a system which performs technical monitoring. In our case we will focus on technical media. 

This article is divided in two parts : how to collect data and build a recommendation system and a second part, how to build a messenger bot which send daily messages and collect data to improve the recommendation. 


## First part : The recommendation system


1. Collect data
2. Clean Data
3. Predict articles 


### 1. Collect data

To manage all this section, we used python. First, build your environnement, you can use Anaconda (https://www.youtube.com/watch?v=pVME6JvdD5g&t=67s) or VirtualEnv. In our case, we used VirtualEnv with PyCharm for the IDE. 

The methode we use to collect the data is the scraping, using the library Scrapy. This is the first lib you need to install. 


**Collect data with Scrapy :** 

1. Create a project : scrapy startproject NameOfTheProject
2. cd /pathToYourProject
3. scrapy genspider NameOfTheCrawler theLinkOfASiteYouWantToScrap.anything

A file "NameOfTheCrawler" should have been created. Open this file and look at the code.

```python
# -*- coding: utf-8 -*-
import scrapy

class NameofthecrawlerSpider(scrapy.Spider):
    name = 'NameOfTheCrawler'
    allowed_domains = ['https://theLinkOfASiteYouWantToScrap.anything']
    start_urls = ['https://theLinkOfASiteYouWantToScrap.anything/']

    def parse(self, response):
        pass
```

Now we're going to fetch the webpage you want to scrap and select the appropriate data : title of the articles, link of the articles and we will add a date for later analysis.

1. Open a scrapy shell with command : scrapy shell
2. Fetch the website (we will scrap medium for the example) : fetch('https://medium.com/topic/artificial-intelligence')
3. If it output 200 it means that is works, then you need to search for the data you want

You can select data by using many informations : id, tag, h1, h2 etc... using response.xpath('YourXpath'). Check the doc if you want more explanation :  https://docs.scrapy.org/en/xpath-tutorial/topics/xpath-tutorial.html

Here is an example of the command we use to scrap Medium :
``` Python
# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

class MediumaiSpider(scrapy.Spider):
    name = 'MediumAI'
    allowed_domains = ['https://medium.com/topic/artificial-intelligence']
    start_urls = ['https://medium.com/topic/artificial-intelligence/']

    def parse(self, response):
        titles = response.xpath('//*[@id="root"]/div/section/section[1]/div[3]/div[1]/section/div/section/div[1]/div[1]/div[1]/h3/a/text()').extract()
        link = response.xpath('//*[@id="root"]/div/section/section[1]/div[3]/div[1]/section/div/section/div[1]/div[1]/div[1]/h3/a/@href').extract()
        now = datetime.today().strftime('%Y-%m-%d')
        clean_approx = []

        for sentence in titles:
            clean_approx.append((sentence.replace(",", "")))

        yield {"Title": clean_approx, 'Link': link, 'Date': now}
```

While you have edit your python file with your corrects xpath, you will be able to crawl the data by typing "scrapy crawl NameOfTheCrawler -o NameOfTheCrawler.csv" in a command shell at the root of your project. 

Then, create a bat file where you activate your environnement and then you run every crawler.

```
@echo off
cmd /k "MyPythonEnvironnement\Scripts\activate & scrapy crawl MediumAI -o MediumAI.csv &  scrapy crawl mediumtech -o MediumTech.csv & scrapy crawl approximatelycorrect -o approximatelycorrect.csv & scrapy crawl kdnuggets -o kdnuggets.csv"
```
It should store all your csv files in the same folder. Now we have to clean all this data to make predictions. 

### 2. Clean data


Since all the csv are stored in the same folder, we can load them and clean them in order to create a simple csv file with all the articles/links/dates. 

This task is done using the class DailyData. There are two functions to clean the csv files because differents websites return data with differents structures.

Then, in the main.py file, we load every file to add it in a huge csv file and then we save this file locally by calling it 'AI_articles_dataset.csv'.

### 3. Predict articles 

Once we have our articles of the day cleaned, we need to select 3 articles for each user depending on his preferences. 

In a firt time, we need to collect many data to build a recommendation system. Since we start with no data, there is a problem called the "Cold Start problem", which mean we have to give to users articles without knowing their preferences.

We will first use a basic neural network with transfer learning (ELMO) for the embbeding layer to make a classification between articles. Each user has his own file with his history of what he has read. We initialize it with a default file and then each day we add the previous day's data depending on whether or not he has read his articles.

The file **TrainModel.py** works in several steps :

1. Add the label from the previous day
2. Preprocessing on the daily data
3. Retraining of the model with new data
4. Predict 3 best articles and upload it on AWS S3

As soon as we have the 3 predicted articles uploaded on S3, the messenger bot is able to send the customized articles for each user. 

## Part 2 Create your own Messenger bot

### Table of Contents

[TOC]

### Prerequisites

Here is what you need to follow this tutorial and set up your messenger bot : 

1. **Node.js**
2. **npm** (node package manager)
3. **Heroku Toolbelt**
4. **Git**
5. **A Facebook page**

Install Node.js
---
![Node.js](https://imagizer.imageshack.com/img921/6763/sqcMd4.png =80x50)

**What is Node.js?**

One day, there was a guy named Ryan Dahl who had the brilliant idea of taking the V8 Javascript engine, it's the one found in the Chrome browser, and using it outside the browser. He created the Node.js platform! It is an open source development platform for executing JavaScript code server-side. Node is useful for developing applications that require a persistent connection from the browser to the server and is often used for real-time applications such as chat, news feeds and web push notifications.

> Download node.js here: https://nodejs.org/en/download/

When your download and set up of Node.js are finished, make sure that Node.js is correctly installed on your machine by simply typing in your command prompt: `node -v`
If Node.js is installed you will see its version.

Install npm
---
![npm](https://imagizer.imageshack.com/img924/8606/6HNgAQ.png =50x25)

**What is npm ?**

npm is the package manager for the Node JavaScript platform. It puts modules in place so that node can find them, and manages dependency conflicts intelligently.

> npm website: https://www.npmjs.com/

npm is distributed with Node.js which means that when you download Node.js, you automatically get npm installed on your computer. Make sure that npm is correctly installed on your machine by simply typing in your command prompt: `npm -v`
If npm is installed you will see its version.

Install Heroku Toolbelt
---
![heroku](https://imagizer.imageshack.com/img923/9985/ive8Fn.png =125x40)

**What is Heroku ?**

Heroku is a cloud platform as a service (PaaS) supporting several programming languages. Heroku, one of the first cloud platforms, has been in development since June 2007, when it supported only the Ruby programming language, but now supports Java, Node.js, Scala, Clojure, Python, PHP, and Go.

> Download Heroku Toolbelt here: https://nodejs.org/en/download/

Make sure that Heroku Toolbelt is correctly installed on your machine by simply typing in your command prompt: `heroku -v`
If Heroku is installed you will see its version.

Install Git
---
![git](https://imagizer.imageshack.com/img924/6743/u52DgE.png =70x30)

**What is Git ?**

Git is a distributed version-control system for tracking changes in source code during software development. It is designed for coordinating work among programmers, but it can be used to track changes in any set of files. Its goals include speed, data integrity, and support for distributed, non-linear workflows.

> Download Git here: https://git-scm.com/downloads

Make sure that Git is correctly installed on your machine by simply typing in your command prompt: `git --version`
If git is installed you will see its version.


## Initialize your local environment

Now that we have all the necessary tools, let's create our local environment. Start by opening a new command prompt.

1. Go to the directory of your choice, in this example I go to my desktop: 
```
cd C:\Users\myUserName\desktop
``` 
2. Create a new folder and give it the name of your bot
```
mkdir myMessengerBot
``` 
3. Go to your Facebook Messenger bot folder
```
cd myMessengerBot
``` 
4. Set up your heroku account with your Facebook Messenger bot folder 
```
heroku login
``` 
5. Update npm
```
npm install npm --global
``` 
6. Initialize npm

When I leave the fields empty it is because you are not required to put something in them
```
npm init

name: myMessengerBot
version: 1.0.0
description:
entry point: index.js
test command:
git repository:
keywords:
author: yourName
license: MIT
``` 
Now, if you have configured your folder with npm correctly, you will be able to see package.json in your myMessengerBot folder there:

![package](https://imagizer.imageshack.com/img921/4219/BNfOWX.png =130x)

7. Install Node.js modules
```
npm install express request $ body-parser —save
``` 
After this step, your myMessengerBot folder looks like this:

![modules](https://hostpic.xyz/files/15568857881773599074.png =160x)

8. Download the Javascript code needed

> **FacebookBot-master.zip** 
> https://codeload.github.com/elmehdimobi/FacebookBot/zip/master
*Thanks to El Mehdi LAIDOUNI for the code.*

And put it on your desktop. You now have these two folders on your desktop:

![package](https://imagizer.imageshack.com/img923/4925/Pjg136.png =200x)

9. Now, unzip the FacebookBot-master.zip file and you will be able to see this:

![package](https://hostpic.xyz/files/15568854432500921323.png =220x)

10. Copy and paste these two files from the unzip fodler to your myMessenger bot folder: 
- Procfile
- index.js

Now, we are here, your local environment **myMessengerBot** is ready: 
![package](https://hostpic.xyz/files/15568861272808899595.png =150x)

## Configure your Facebook developer account

Now that our local environment is ready, let's configure our developer facebook account.

1. Go to the Facebook developers website
> https://developers.facebook.com/apps/

2. Create a new app (click on "Add a new app")
3. Go to "Messenger" section and clikc on "Get started" button
4. In the "Access token" section, select your Facebook page
5. Copy your token
6. Paste it in your index.js file at the right place:
```
var token = "entrez votre token ici"
```
> *Translation: "entrez votre token ici" = "enter your token here"*

## Configure your Heroku account

Now that our local environment is ready and our facebook developer account is ready too, let's configure our heroku account.

1. Go to myMessengerBot folder on your desktop and open a cmd
2. Initialize git
```
git init
```
3. Create your app (bot) on heroku by enter your app name
```
heroku create myMessengerBot
```
So you will get the callback URL of your application, which you can copy now in your clipboard, it looks like:

> Callback URL: https://myMessengerBot.herokuapp.com/
> 
4. Now, if you go to Heroku dashboard, you will see your app
> https://dashboard.heroku.com/apps
5. Before continuing, make a first commit to heroku to initialize your application
```
git add .
git commit -am "your message"
git push heroku master
```

## Link Heroku with Facebook

1. Go back to your facebook developer dashboard
> https://developers.facebook.com/apps/
2. Click on your app
3. Go to the "Messenger" tab
4. Click on "Settings"
5. Go to "webhooks" section
6. Click on "Edit events"
7. 


## Appendix and FAQ

:::info
**Find this document incomplete?** Leave a comment!
:::

###### tags: `Messenger` `Bot` `Node.js` `npm` `Heroku` `Facebook` `Javascript`
