# becgi
becgi is a BMS event venue based on Python 3.5.0 using Flask and PostgreSQL.  
This code is being used for the BMS event [Be-Music West](http://bmwest.herokuapp.com/).  
It is extensible if you wish to add new fields, as you only need to add new rows in the database and make changes to the htmls.  

becgi supports the basic things needed such as:  
* Generic fields
  * Artist
  * Title
  * BGA Author
  * Email
  * Download URL
  * Email
* Fake Artist Name (Used for pseudonyms, displayed until after impression period.)
* Automatic opening and closing of venue (Submissions and Impressions individually)
* reCAPTCHA for submissions and impressions
