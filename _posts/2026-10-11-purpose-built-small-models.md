---
title: Purpose-bullt small local models deserve more love
date: 2026-10-11
image: /content/images/2026/butter_bot.jpeg
excerpt: Applied AI these days do a very specific job with a large generalized model. Many times its not really necessary
tags: ["english","ai"]
---
Lets first set the premises here. AI as we know today is often referred to Large language models (LLM) like Claude, chatgpt or gemini. Many of the models we are going to talk about are not LLM. They are what I like to refer to as pre-llm defination of AI. And you might not have known of noticed that they had been part of our hardware and software since long before the first LLM was conceived. But again, this conversation is more relevant now because AI is a household name, and with agentic engineering, its now easier than ever to find or train a ML model that suits your needs perfectly. I will share my real life case studies on this as well.

One of my favorite animated TV shows is Rick and Morty. In one of its episodes Rick makes a seemingly sentient robot on the dining table. 

**When the robot asks Rick:** 
what is my purpose? 

**Rick answers:** you pass the butter. 

<iframe src="https://giphy.com/embed/Fsn4WJcqwlbtS" width="480" height="269" style="" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>


The reason I brought it up because as funny as this scene is, this can be interpreted either as a wasted potential for the robot or if the robot is purpose-built for passing the butter it's going to do that better than anyone else. 

But I am getting ahead of myself. Let's start with some invisible examples. Things like email spam filters, automatic number plate recognization system, Your camera's subject-detection autoficus, even Adobe photoshop's content-aware fill (relevant later) are a few examples of purpose-built models in action. Your smartphone might be running 10's of them every day since the dawn of smartphones without making itself known. the secondary point is: AI had been everywhere, since a long time. 

The reason they are in aboundance is because they are very small. In fact in the grand scheme of things they can be considered tiny. And they require very little resource to run. For that exact reason, they don't need a massive data center to run and instead can be run locally in your computer, a smartphone, in your web browser or even in a capable microcontroller. 

The very first time I worked with a ML model was back when I was doing my bachelor in computer science. One of my professors asked me to help a senior to make a smarter surveillance system as part of their final project. The idea was to only record when there is a motion. Now this might sound something common these days, back then, it was a novelty. And we trained our own ML model to reliably detect motion in blurry low-res CCTV footages. In my professional life, I helped one of my teammates to train a model that can detect forged id cards.

Recently, I started working on my hobby projects again. And one of the projects that I really love and care about is [35mm photo](https://35mm.photo/). It's a photo editor. And if you ask me I would say it's one of the best browser based Adobe lightroom alternative out there. do give it a try btw. But the reason I brought it up is because of it's architecture. It runs entirely off-of github pages, so it doesn't have any backend whatsoever. 

![35mm photo](/content/images/2026/35mm_logo.png)

Initially I thought all the ambitious features I planned for this, specially things that involve AI might not be possible. But then I got an idea, how about I try using models that are small enough to run in a browser. And that's exactly what I did. and *It runs three in-browser models for three different tasks*.

##### The first one is AI subject detection
This is the first model I used. It uses the model [U²-Netp](https://github.com/xuebinqin/U-2-Net). I converted it from float32 to float16 precision and the model size shrinked down to **2.3MB**. With this 2.3MB model it can detect a wide range of subjects including humans, animals, cars etc. You can see it in action in the mask tool of the app. If you add a subject mask, it does a one-time model download and then runs the subject detection in the photo. 

![Subject detection in action](/content/images/2026/feature-subject.png)

##### Second model I brought in is for smart fill
AI subject detection gave me so much confidence that I immediately started looking into AI cleanup/object deletion on a smart heal tool. I remember when Adobe introduced content-aware healing tool back around 2010 I was amazed! It was probably one of the early demonstrations of what AI is moving towards. So this feature or something that's close to it had always been in my wishlist for features. So I looked into multiple models that could potentially do it and ended up using [MI-GAN](https://github.com/Picsart-AI-Research/MI-GAN). This model is **14.2MB**. And it can remove quite large things from your photo gracefully. I was surprised at how well it works for its size. 

![Smart fill](/content/images/2026/retouch-canoe.jpg)

##### Third model I used is for upscaling images
This I was not sure if it was possible. because I've upscaled images with models like gemini. So I went into it with low expectations. But then I found [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN). All together the model is **31.9MB** in size. but it can upscale a low-res image up to 4x its actual size. Even works on a cropped section of an image. And for the size and amount of resource it uses, it does a fair enough job.  

But the time I spent on huggingface and github looking into small purpose built models the more they amazed me. There are hunderds of models for detection, enhancement or generation. And its now also easier than ever to test and build on top of them. Or if you are brave enough: Train your own. 

##### So how do I approach to find and use purpose built models. 
I think there are many frameworks and writeups on the "how" aspect of it, mostly technical details. I will share my thought process. When I come across a problem, the solutions I think of might involve the system to be smart. Now The question I ask myself is: Does it have to be generally smart of just have to be smart enough to do one thing very well. If the answer is: yeah one thing it is, then I would look for a small model first. If there is a model I would try using it. If there isn't I will check if I have enough data to train a model. If I do, I would estimate how diffucult or expensive it would be to train a model. If all of the above does not work Only then I would approach larger generic models. 

This approach so far helped me push the web browser to crazy lengths. Helped me ship features that would seem impossible from the browser, at least in the frontend itself. Do give them a try. It might help you too.






