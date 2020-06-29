***************************************
AF score specification - version 4.
***************************************

R: Quan Tran

Modification date: 
   * 2 - June - 2020 (v4.0) 
   * 3 - June - 2020 (v4.0)

Agenda
======

1. `Introduction <#introduction>`__
2. `Context <#context>`__
3. `Scope <#scope>`__
4. `KPIs <#kpis>`__
5. `Limitation <#limitation>`__


1. Introduction 
================

Amplifcation factor (AF) is one of :math:`3` metrics of Advosights used
to measure the **amplification of an individual in a specific network
where compagin are launched**.

Generally, AF score requires :math:`3` kinds of data: *User attributes*,
*User behaviors* and *Posts* (Figure below). These data forms the
structural data called **Directed Knowledge Graph**.

.. figure:: https://i.imgur.com/yTB518v.png
   :alt: af\_input\_output

   af\_input\_output

For a brand
------------
Generally, the purpose of AF is to increase sale of business. In
particular, by measuring the AF of users, we can find out: \* Which
users are the most influencers in a specific network \* Predict how many
users are influenced by one given user \* Predict which direction of
information when a user submit a new post

    *For example, brand X owns a small community in Facebook (e.g, a FB
    group of X). They aim to find out which users are most influencers
    among ones to make them as potential KOLs. Thanks to their large and
    fast diffusion, when they submit posts mentioning to X, other users
    are able to easily get the information very quickly.*

For a specific user
--------------------
When taking part in an advocated community of a brand, a user intents to
increase the amplication factor as much as possible due to: \* The user
are going to be more potential to be hired by the brand \* AF model is
able to predict how much user's new post will be amplified in his
community \* By monitoring the AF score, users are able to know things
needs to improve \* User can directly measure AF to an other specific
users

    *For example, user Y is in an advocated member in group G of brand
    X. AF score is calculated by attributes of Y and others users in G.
    When user Y intents to submit a new post, Y is able to be predicted
    who users are likely to be influenced by that post. Y is also able
    to measure AF to a specific user Z in G to know whether Z are
    influenced by Y or not*

2. Context 
===========

AF score requires the commuinty networks among users. In particular, it
acquires **set of users which some of them connected to each others** to
form a **graph network** (see below figures).

.. figure:: https://i.imgur.com/IxqBzxn.gif
   :alt: graph\_example

   graph\_example
Therfore, our AF score is assumpted to formulated by *user's
attributes*, *user's relationship* and *the corresponding posts*: \*
**User's attributes** are behavior of a user, these includes their
public information and their interaction on some specific social
networks in our purpose.

-  **User's relationship** are the relationships between the concerned
   user and the others in a network.

-  **User's posts** are the content of previous posts has been submited.

| The figure below visualizes the dependence of AF on user's
relationship (user's attributes) and posts.

.. figure:: https://i.imgur.com/Ob1a8Q5.png

| AF\_assumption

Since we defined our problem as a knowledge graph which handles the
relationship among users, there are :math:`3` things need to be
concerened: *users' attributes*, *users' relationship* and *their
corresponding posts*.

User's attributes
~~~~~~~~~~~~~~~~~

Users' attributes contains **their public information** and **behavior**
in an social network. For a specific social context, these attributes
can vary depends on the supplied services of that social network

-  version 4.0:
   The current version is being experimented on Facebook database. As a
   result, we concern on following :math:`7` attributes (not including
   **id** of users:

   -  **total\_followers**: number of followers
   -  **total\_friends**: number of friends of a user
   -  **books\_count**: number of books user
   -  **films\_count**: number of films user
   -  **music\_count**: number of music user
   -  **restaurants\_count**: number of restaurants user
   -  **sex**: gender (:math:`3` if private)

*All the missing values were completely filled by mean of the dedicated
ones*

User's relationship
~~~~~~~~~~~~~~~~~~~

Is the way we define the relationship among users depending on specific
social network.

-  | version 4.0:
   | The current version is being experimented on Facebook social
   network. As a result, **we define the relationship when a user
   reacts, comments or shares on any post from other user** (detail in
   below figures). Then, we calculate the **weight of relationship** as
   below formula. The underlying weights are partly referenced from
   version 2.

   ::

                             weights = 0.1*number of reactions + 0.3*number of comments + 0.6*number of shares

.. figure:: https://i.imgur.com/l0iqTKO.png
   :alt: edge\_definition

   edge\_definition
User's posts
~~~~~~~~~~~~

| Are all the attributes of a specific user's posts depending on
specific social netork. **By crawling posts of users, we are able to
analyse useful features such as which topics user interested in, writing
style of user, etc**. This also helps us know which style of post that
user can be easily influenced, since each user will prefer a specific
one. \* version 4.0:
| We currently focus on posts' contents that user submited

3. Scope
========= 

Below is all attributes requirements and their corresponding scope

+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Name                       | Scope                                                                                                                       | Requirement                                                                                                                                                                             |
+============================+=============================================================================================================================+=========================================================================================================================================================================================+
| Number of users            | :math:`> 100`                                                                                                               | - Including KOLs and users who interact with them. - All users must have at least :math:`1` connection with other user (avoid isolated user)                                            |
+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| User attributes            | :math:`7` attributes: total\_followers, total\_friends, books\_count, films\_count, music\_count, restaurants\_count, sex   |                                                                                                                                                                                         |
+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Number of posts per user   | :math:`> 10`                                                                                                                | Posts have: - Content - Number of reactions, shares, comments - Range of time: at least :math:`> 10` posts :math:`1` latest month - Information of corrsponding user ids who interact   |
+----------------------------+-----------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. raw:: html

   <!-- # 3. Main approach -->

4. KPIs 
========

-  [x] AF score version 4. proposal
-  [x] Overall data analytics
-  [x] Data preprocessing and transformation
-  [x] Training user embedding model
-  [ ] Training post embedding model
-  [ ] Preparing training data for AF model
-  [ ] Training AF model
-  [ ] Release

5. Limitation 
==============

-  Since AF score takes **deep learning** into account, the efficency of
   AF score depends on the quality of data source and preprocessing
   method. *For the current version (4.), we just take very simple
   preprocessing method.*
-  User's attributes are invariance, depends on specific kind of social
   network.
-  User's attributes reach affordable number of attributes.

.. |AF\_assumption| image:: https://i.imgur.com/Ob1a8Q5.png