# becgi
becgi is a BMS event venue based on Python 3.5.0 using Flask and PostgreSQL.  
This code is being used for the BMS event [Be-Music West](http://bmwest.herokuapp.com/).  
It is extensible if you wish to add new fields, as you only need to add new rows in the database and make changes to the htmls.  

becgi supports the basic things needed such as:  
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

There are still a good amount of features currently lacking that are planned to be implemented for the next event:
* Embeds for SoundCloud, YouTube, Nico Video
* Stagefile
* Form for expressing intent to join

Right now the Impression Score is using the log10 calculation that Be-Music West uses.  
This can easily be changed by adjusting the code to your liking.  
**To be able to run this code you need to create a config.py containing reCAPTCHA authentication keys.**
