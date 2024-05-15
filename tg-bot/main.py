import os
import replicate

training_id = os.getenv("REPLICATE_TRAINING_ID")
training = replicate.trainings.get(training_id)

print(training)

training.reload()

prompt = """[INST] <<SYS>>\
Use the Input to provide a summary of a conversation.
<</SYS>>

Input:
Harry: Who are you?
Hagrid: Rubeus Hagrid, Keeper of Keys and Grounds at Hogwarts. Of course, you know all about Hogwarts.
Harry: Sorry, no.
Hagrid: No? Blimey, Harry, did you never wonder where yer parents learned it all?
Harry: All what?
Hagrid: Yer a wizard, Harry.
Harry: I-- I'm a what?
Hagrid: A wizard! And a thumpin' good 'un, I'll wager, once you've been trained up a bit. [/INST]

Summary: """

output = replicate.run(
  training.output["version"],
  input={"prompt": prompt, "stop_sequences": "</s>"}
)
for s in output:
  print(s, end="", flush=True)