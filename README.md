# becgi
becgi is a BMS event venue based on Python 3.5.0 using Flask and PostgreSQL.  
This code was first made for the BMS event [Be-Music West](http://bmwest.herokuapp.com/).  
Its open source nature allows you to customize it for your own needs.

becgi supports the basics such as:  
* Generic submissions fields
  * Artist
  * Title
  * BGA Author
  * Email
  * Download URL
  * Email
  * Comment/Description
* Fake Artist Name (Used for pseudonyms, displayed until after impression period.)
* Automatic opening and closing of venue (Submissions and Impressions individually)
* reCAPTCHA for submissions and impressions
* Impressions
  * Name
  * Comment
  * Score
* Multiple event support
* Markdown Formatting (via Database)


**To be able to run this code you need to create a config.py containing reCAPTCHA authentication keys and a secret key. See the included example config.**
