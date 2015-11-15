.. _api_algorithms_classful:

Classful Queuing Disciplines
============================

.. contents:: Table of Contents
   :depth: 4

HTB
---

HTB is a type of QDisc which allows to set a rate and burst, with priorities
between classes. You can get more informations `here
<https://en.wikipedia.org/wiki/Token_bucket#Hierarchical_token_bucket>`_.


Empty HTB class
~~~~~~~~~~~~~~~

.. autoclass:: pyqos.algorithms.htb.EmptyHTBClass
   :members:
   :inherited-members:


Basic HTB class
~~~~~~~~~~~~~~~

.. autoclass:: pyqos.algorithms.htb.HTBClass
   :members:
   :inherited-members:


Root HTB class
~~~~~~~~~~~~~~

.. autoclass:: pyqos.algorithms.htb.HTBClass
   :members:
   :inherited-members:


HTB filter
~~~~~~~~~~

.. autoclass:: pyqos.algorithms.htb.HTBFilter
   :members:
   :inherited-members:


HTB filter with FQCodel
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: pyqos.algorithms.htb.HTBFilterFQCodel
   :members:


HTB filter with PFIFO
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: pyqos.algorithms.htb.HTBFilterPFIFO
   :members:


HTB filter with SFQ
^^^^^^^^^^^^^^^^^^^

.. autoclass:: pyqos.algorithms.htb.HTBFilterSFQ
   :members:
