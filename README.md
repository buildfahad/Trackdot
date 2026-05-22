 **TrackDOT** (work in progress)
#### Video Demo:  <URL https://youtu.be/uoPrd7w4RK4>
#### Description: My web app can take your riot account game name and tag and fetch your profile information and most recent matches you played. Moreover it can fetch top 10 players from all 3 of the major regions EU, NA and APAC. You can create an account on the website and login.

STACK USED: HTML,CSS (Boostrap), Python (Flask), SQLite, and a bit of JS.

Let's start by talking about what functionality I built into the app.
I wanted the app to be good enough to be used actually, however simple it might be it needed
to have some functionality some sort of usefulness, although not much I believe being able to
see your profile or other person's by just using their in-game name and also being able to
check their most recent matches without logging in to their account is pretty useful to some
extent anyway. So, what does it do? So, when you visit the website or localhost (not yet
deployed) you are met with a login screen, why not a homepage? well I added a different use
to that, I remembered from finance problem we used something called decorators to make login
necessary for some routes well index is one such route. So, you either login or if you are new
you create an account and login (yes, I'd rather have the user login after creating so they
remember the logs lol). You are then redirected to index or homepage, there you see an input
field and a submit button. This is where you enter your riot games id and tag (kind of like old
discord idtags) you know if you are a gamer. It then sends a get request to the player route and fetches the data requested and
takes you to the next page "Player" you then see your profile info like idtag your level and your player card your current rank
what region the account is based in for example NA, EU or AP. Below that you see your most recent
matches. Btw you can also see information about any other player you know Idtag of.
This route also adds session variable for idtag and stores and shows it on the navbar, to click again. It is replaced by the new one if you search for a new player.
That was the third thing on the navbar now let's go to 2nd thing because we jumped lol.
That is Leaderboard, well as the name suggests it's a list of top players from certain regions.
I only added 3: EU, NA and AP. you visit the page and by default it loads 10 of the top players in that region. there you also see 3 buttons with region names you can press and go
to any region and get top 10 players from that region. 

How do I do this? Well, if you took CS50 to remember we learned about APIs. and also used one such thing in finance problem, although not this complicated. I used an API to fetch Player data from Riot Games and display on the page using jinja.
When I was done with leaderboard I realized it takes a lot of time after clicking the button to get the data because there are 10 players and it felt really annoying so what I did was save the data in database the first time and just check if it's not older than a certain period then just use that to populate the page. I decided on 1 day although in a real app with users that would not be ideal maybe few minutes like 5 or 10. So now it loads almost instantly, of course after the first load in last 24 hours.
The Profile information and match data is fetched the same way. The rank info is not available in account info endpoint, so I used matchlist endpoint and use that as the current rank using the puuid.
What does the match info divs show? Yes, I used a div for each match instead of a table, I felt it was much prettier this way. SO, it shows the map, which game mode was it eg. "Spike Rush", the agent which our player used, the result of the match meaning whether it was lost or won, KDA (Kills, Deaths and Assists) of our player and the date and time the match was played on. Additionally, I added if logic in the div style to use a transparent background with green or red tint for win or loss respectively.
Alright let's talk about next navbar item, the logged in username yes I display the current user logged in. It felt confusing at first because some pages I was only redirecting to would not be able to access it because you can only pass data render_template. I mean you can do it with redirect too but that felt weird. So, I found this thing called context processor, this thing is great, you can inject the username directly into the app context and access it using jinja. Pretty neat.
Then lastly you can also logout of the app.

Now let's talk about design.
Although I liked the simplistic design in finance I just didn't vibe with it as much. I like dark themes and a single-color accent, so I went with a dark purplish grey for background and a purple color accent. Even though I used bootstrap I had to do a lot of custom CSS to alter the table colors and whatnot spent a lot of time searching and reading docs failing over and over. Let me tell you front end seemed much harder to control than backend T_T. Also, I used JS to add a typewriter effect into the Logo text. I once saw it in a website, and it looked cool. I just added it to the dom loaded function so the page loads first and then our effect takes place. I did a simple search on how to do it on google and it was pretty straightforward to just alter it and make it work for me. 
The front end was a real pain; I got so annoyed by this player info div I need to adjust I wanted a smaller div for info and right next to it a wider div for player card image. it took a lot of time and wish I didn't obsess over it looking good lol. to the smaller div I added a transparent gradient in CSS so it looks cool. I added custom CSS classes to adjust all these things and also to change the color of table. I added outline buttons that get full when hovered.
I could go into much detail and nitty gritty of routes and all but I think it's enough for now, I will try to keep adding stuff into this and maybe release it as full app eventually haha ambitious I know but whatever. Ty if anyone read it, I don't think anyone will but if you did tysm bye!
