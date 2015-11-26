.. _tutorial_part2:

Part 2: Defining root qdisc
===========================

This part describes how to attach a qdisc on the interface, depending of the
case of QoS type you want (classful or classless).

.. contents:: Table of Contents
   :depth: 2


Structure
---------

For this example, as the goal is only to shape the internet traffic, I have
split the rules in two folders: ``download`` and ``upload``. The
``__init__.py`` of each folder will define the root QDisc and HTB class for the
interface it targets, and then add this root class to the running list of our
application.

This structure has worked for me for my setups with HTB, but I do not really
recommend it for classless setups. As usual, do not feel restricted by the
structure given here, and feel free to adapt it.
