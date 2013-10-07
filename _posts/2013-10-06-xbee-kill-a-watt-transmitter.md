---
layout: post
title: "XBee Kill-a-Watt Transmitter"
description: "Building a second XBee Will-a-Watt transmitter to wirelessly record power consumption"
category: articles
tags: [hardware hacking, xbee]
og:
  image: 'xbee-kill-a-watt-transmitter.jpg'
  type: 'image/jpeg'
  width: '628'
  height: '402'
comments: true
---

For a few months I have had the parts to build another transmitter for my [XBee / Kill-a-Watt power measuring system](http://www.ladyada.net/make/tweetawatt/).  Since I've already chronicled the overall system but didn't have any photos of the process, this post will provide the pretty pictures I lacked before.

# The Parts
I started with parts from Digi-Key and Adafruit.  At the outset, you don't start with much.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-parts.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-parts.jpg"></a>
  </figure>
  <figcaption>The Adafruit XBee Adapter Kit and Kill-a-Watt.</figcaption>
</div>

All the parts aren't pictured above, but here's the full parts list (save a few resistors, heat shrink and ribbon cable):

* [Adafruit XBee Adapter Kit](http://www.adafruit.com/products/126)
* [XBee Series 1 with U.FL connector](http://www.digikey.com/product-search/en/XB24-AUI-001-ND)
* [2.4 GHz RF Antenna](http://www.digikey.com/product-search/en/W1049B050/553-1826-ND)
* [P3 Kill-a-Watt](http://www.newegg.com/Product/Product.aspx?Item=N82E16882715001)
* [50V, 1A Diode](http://www.digikey.com/product-detail/en/1N4001/1N4001FSCT-ND)
* [220UF 6.3V Capacitor](http://www.digikey.com/product-detail/en/ECA-0JM221/P5112-ND)
* [10000UF, 6.3V Capacitor](http://www.digikey.com/product-detail/en/ECA-0JM103/P5120-ND)
* [Green LED](http://www.digikey.com/product-detail/en/MV64530/1080-1128-ND)

It would have been easier to purchase the add-on kit from Adafruit, but I had enough parts lying around _and_ wanted to get the XBee module with the U.FL connector to as receiver XBee.  After the initial build I found that the XBee Series 1 that ship with the Adafruit kits could barely communicate between adjacent rooms.

# The Easy Part

There are several small parts and headers you solder onto the XBee adapter board before you start doing more hacky stuff.  Here's a picture at about that point.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-easy-complete.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-easy-complete.jpg"></a>
    <figcaption>XBee adapter board with the easy soldering complete.</figcaption>
  </figure>
</div>

You can see how short those 10-pin headers are from the first picture.  Getting these parts to fit under that height is easy, but the next parts, no so much.

# Finishing the Transmitter

The next several steps are kinda messy.  You need to solder second resistors onto two already on the board and the 220uf capacitor gets bent underneath where the XBee module will sit.  The leads coming from those resistors get soldered onto the leads from the 10000UF capacitor.  The diode gets added to the positive terminal of the capacitor and everything gets covered in heat shrink.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-parts-soldered.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-parts-soldered.jpg"></a>
    <figcaption>XBee parts soldered and ready to go into the Kill-a-Watt.</figcaption>
  </figure>
</div>

Instead of separated ribbon cable I used solid wire.  If I make another transmitter, I would use braided wire (or separated ribbon cable) due to it's flexibility.

# Integrating into the Kill-a-Watt

The next step is to open up the Kill-a-Watt and figure out whether you have a P4400 or a P4400.1.  The later has a smaller version of the 2902 op-amp which is located _behind_ the Kill-a-Watt display.  The leads for the display can be seen in a line between the two clips in the photo below.  the display must be flush against these for the Kill-a-Watt display to function correctly, and with the tight fit, getting the leads from the op-amp around the board to the backside of the Kill-a-Watt housing can be a challenge.  It's difficult to see in the picture below, but I shaved a millimeter or so off the left side of the PCB.  The "R" in R8 is partly shaven off.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-board-with-leads.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-board-with-leads.jpg"></a>
    <figcaption>The lead wires from the XBee soldered to the 2902 Op-Amp.</figcaption>
  </figure>
</div>

I also used a razor blade and chisel to whittle away some of the inside of the plastic Kill-a-Watt housing.  It's difficult to see, but absolutely essential to being able to re-seat the PCB in a way that allows the display leads to connect correctly.  There are two supporting plastic pieces in the middle of the right side of the PCB, which is the best spot to whittle the plastic.  Additionally, I recommend using something like [3M Command Hook backing tape](http://www.digikey.com/product-detail/en/17026/3M12109-ND) to adhere the XBee and capacitor to the housing so they don't rattle around.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-in-housing.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-in-housing.jpg"></a>
    <figcaption>The XBee transmitter ready to be sealed into the Kill-a-Watt.</figcaption>
  </figure>
</div>

I would recommend testing before you seal up the unit.  Also, don't forget to program the XBee to have a different ID than any other transmitters you may have.

# All Done!

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/xbee-kill-a-watt-transmitter-complete.jpg"><img src="{{ site.url }}/images/xbee-kill-a-watt-transmitter-complete.jpg"></a>
    <figcaption>Fully assembled XBee Kill-A-Watt transmitter.</figcaption>
  </figure>
</div>

The third-hand tool gives the transmitter one last hug before the transmitter goes into service.
