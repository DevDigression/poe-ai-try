import os
import replicate

training_id = os.environ["REPLICATE_TRAINING_ID"]
training = replicate.trainings.get(training_id)
print(training)

training.reload()

prompt = """[INST] <<SYS>>\
Use the Input to provide a summary of a conversation.
<</SYS>>

Input:
Nikhil: I'm still not understanding this. Why is it so hard to display the birthday date on the settings page? Why can't we ge this done this quarter?

Ben: Look, I'm sorry we've been over this. It's the design of our back-end. First, we have to go to Bingo service. See, Bingo knows everyone's name-o. So we get the users ID out of there and from Bingo we can call Papaya and NBS to get that user ID and turn it into a user session token. We can validate those with LMNOP and then once we have that we can finally pull the user's info down from Raccoon.

Nikhil: But couldn't the Raccoon team basically-

Ben: No! Raccoon isn't guaranteed to have that info. Before we do this we have to go to Wingman and do a query to see if they are willing to take it to the next level (or if they're just playing the field).
Wingman is cool, but he doesn't store any user info himself. He has to reach out to other user info provider services like RGS, BRB-DLL, Ringo 2, and BLS. 
But how does it know what all the user provider services are? Well, for that it has to go to Galactus - the all-knowing user service provider aggregator. While Galactus has omniscient knowledge of all current user info providers, it doesn't have future sight or knowledge of past user info providers, so it expects a time range.
To get all the current user info providers, we need to pass a time range with the current time and a time representing the end of the universe, which we get from EKS, our Entropy Kaos Service. EKS is being deprecated at the end of the month for Omega Star; but Omega star still doesn't support ISO timestamps like they said they would a month ago. So until Omega Star gets their stuff together, we're blocked! We can't get sign up for our use case; we can't use EKS; there's nothing we can do!
So Galactus won't be able to find our new Birthday Boy provider which means Wingman won't know how to talk to anybody which means I won't be able to find true love and I'll die alone! I'll die alone!  Without ever knowing love! Without ever knowing it's my birthday!
We're blocked, okay? We're blocked you sad, pathetic little product manager! You think you know what our users want? You know nothing of my pain - Of Galactus' pain!
You think you know what it takes to tell the user it's their birthday! You know nothing! Delivering this feature goes against everything I know to be right and true, and I will sooner lay you into this barren earth than entertain your folly for a moment longer!

Nikhil: Alright, so clearly this is a blocker! No problem, we'll push this out another two to three years or so. I learned a lot today. I love Galactus. We'll talk next week about adding middle names to the profile.

Summary: """

output = replicate.run(
  training.output["version"],
  input={"prompt": prompt, "stop_sequences": "</s>"}
)
for s in output:
  print(s, end="", flush=True)