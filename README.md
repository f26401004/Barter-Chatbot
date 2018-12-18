# Barter

![](https://i.imgur.com/LJX9OOa.png)

`──回到最原始、最自然的生活，讓我們一起以物 yee 物吧！`
`──Back to the most primitive and natural life, let us start with barter!`

這是一個提供以物易物的粉絲專頁機器人，提供使用者向資料庫輸入自己要拿出來交換的物品資訊，並且提供查詢的機制，使用者可以向機器人查詢前 5 個別人要拿出來交換的物品資訊。

物品被分為 ["食物或飲料", "3C 或電子產品", "衣物", "化妝用品", "書籍", "雜物"] 6 種，使用者在輸入自己要交換的物品時、或是查看最新交換物的物品時都必須選擇。

另外當使用者遇到信用不佳或交換的過程品質不佳的情況時，可以向機器人輸入交換者的 link 檢舉。被檢舉的交換者將會下降自身的信用程度，信用程度低於 60 則無法繼續使用本服務。

This is a fan-specific page robot that provides bartering. It provides users with the information to enter the information they want to exchange, and provides a query mechanism. The user can query the robot for the information of the first five others.

The items are divided into six categories: ["food or drink", "3C or electronic product", "clothing", "cosmetic", "book", "garbage"], when the user enters the item to be exchanged, You must choose when you view the items of the latest exchange.

In addition, when the user encounters a situation in which the credit is not good or the process of the exchange is not good, the exchanger's link can be input to the robot. The audited exchanger will reduce its credit, and credits below 60 will not continue to use the service.

## Prerequisite

1. [Firebase](https://firebase.google.com/)

![](https://i.imgur.com/pkm5kPX.png)

2. [Google Cloud Platform](https://cloud.google.com/)

![](https://i.imgur.com/H3fVrXJ.png)

3. [Ngrok](https://ngrok.com/)

![](https://i.imgur.com/xY2u57u.png)

4. [Flask](http://flask.pocoo.org/)

![](https://i.imgur.com/VtyID6H.png)

5. [Pytransition](https://github.com/pytransitions/transitions)



### Install Dependency

`pip install -r requirements.txt` or
`pip3 install -r requirements.txt`

### Screte Data

`ACCESS_TOKEN` -> `粉絲專頁存取權杖`
`EMPTY_STRING` -> `判斷使用者的輸入是否為字元，如果不是，則 message["text"] 會直接被附值為 EMPTY_STRING`
`GOOGLE_APPLICATION_CREDENTIALS` -> `Firebase 存取權限 JSON 檔`
`PAGE_TOKEN` -> `粉絲專頁自動發文權杖`

`ACCESS_TOKEN` -> `Fan page access tokens`
`EMPTY_STRING` -> `Determine whether the user's input is a character. If not, message["text"] will be directly appended to EMPTY_STRING`
`GOOGLE_APPLICATION_CREDENTIALS` -> `Firebase access JSON file`
`PAGE_TOKEN` -> `Fan page automatic posting scepter`

## Database Structure

![](https://i.imgur.com/aWb3GcB.png)

因為必須讓所有的使用者和機器人對話時能各自擁有不同的狀態，因此必須使用 database 儲存每個使用者的狀態。
然而為了達到 realtime 的服務品質，因此選擇 Google 的 Firebase Realtime Database 實作。其本質便為一個極大的 JSON 檔，使用上而言只需要分清楚每個 field 的功能便可以多用途使用。

Because all users and robots must have different states when talking to each other, you must use database to store the state of each user.
However, in order to achieve realtime service quality, choose Google's Firebase Realtime Database implementation. The essence is a huge JSON file. In terms of use, it only needs to distinguish the function of each field and it can be used for multiple purposes.

---

**使用者狀態相關 About User State**

* uid(role=unknow)
    * name
* uid(role=proposer)
    * name
    * state
    * data
        * name
        * description
        * number
        * type
* uid(role=checker)
    * name
    * state
    * data
        * type
        * items
            * name
            * description
            * number
            * type
* uid(role=blocker)
    * name
    * state
    * data
        * url

**所有使用者的資訊紀錄 About User Info**

* uid
    * credit
    * link
    * name

**交換物物品資訊相關 About User Item Info**

* type
    * uid
        * name
        * description
        * number
        * image_url
        * proposer
        * timestamp

## Finite State Machine

![](https://i.imgur.com/AYk72TL.png)

## Usage

起始的狀態為 initial
一旦開始對話後根據對話內容會自動轉移狀態，轉移狀態的條件如下：

The initial state is initial
Once the conversation is started, the status is automatically transferred according to the content of the conversation. The conditions for the transition state are as follows:

#### General

* initial
    * input: 任意字串
    * transition: initial -> unknow
* unknow
    * input: "我要提議"、"最近夯什麼"、"我要檢舉"
    * transition:
        * "我要提議": unknow -> proposer_state1 | unknow -> proposer_state2
        * "最近夯什麼": unkow -> checker_state1
        * "我要檢舉": unknow -> blocker_state1

---

#### Proposer

* proposer_state1
    * input: 任意字串(非貼圖、附件)
    * transition: proposer_state1 -> proposer_state2
* proposer_state2
    * input: 任意字串(非貼圖、附件)
    * transition: proposer_state2 -> proposer_state3
* proposer_state3
    * input: ["食物或飲料", "3C 或電子產品", "衣物", "化妝用品", "書籍", "雜物"]
    * transition: proposer_state3 -> proposer_state4
* proposer_state4
    * input: 任意數值(非貼圖、附件)
    * transition: proposer_state4 -> proposer_state5
* proposer_state5
    * input: 任意字串(非貼圖、附件)
    * transition: proposer_state5 -> proposer_state6
* proposer_state6
    * input: 圖片附件
    * transition: proposer_state6 -> unknow

---

#### Checker

* checker_state1
    * input: ["食物或飲料", "3C 或電子產品", "衣物", "化妝用品", "書籍", "雜物"]
    * transition: checker_state1 -> checker_state2
* checker_state2
    * input: 任意數值(非貼圖、附件)
    * transition: checker_state2 -> unknow

---

#### Blocker

* blocker_state1
    * input: 任意字串(非貼圖、附件)
    * transition: blocker_state1 -> unknow


## Reference

[TOC-Project-2017](https://github.com/Lee-W/TOC-Project-2017)
[Graphic Designer - XianXingZhe](https://www.instagram.com/xianxingzhe1106/)
