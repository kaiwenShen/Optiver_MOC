# Some Facts About MOC 
1. MOC is a 5-minute auction at the end of the day.
2. NASDAQ starts at 3:50 and NYSE starts at 3:45 (recently changed to 3:50)
3. NASDAQ operates fully electronic, NYSE is hybrid.
4. MOC orders and LOC orders are accepted before the start of the closing auction.
5. no modification or cancellation of MOC orders after 3:55. LOC can enter until 3:58 p.m.
6. Imbalance-only orders are accepted until 4:00 pm, which are Nasdaq BBO prices at the close.
7. Buy IOs execute only if closing prices are above the 4:00 p.m. ask
price. Sell IOs execute only if closing prices are below the 4:00 p.m. bid
price.
8. a very nice introduction provided by the optiver team: [link](https://www.kaggle.com/code/tomforbes/optiver-trading-at-the-close-introduction)
9. the target is likely been transformed or truncated. [link](https://www.kaggle.com/code/mihailturlakov/optiver-auction-eda-dense-data-wap/notebook)
# Factor Ideas:
1. volatility weighted synthetic index: Target computation have its own synthetic index computation component.
2. historical beta: correlation between stock and index
3. AR1: target usually bonce between two periods. 
4. volatility: historical volatility of the stock will continue
5. order book imbalance shift around: how many times order books imbalance changes, indicates disagreement between buyers and sellers.
6. order book imbalance shift magnitude: small difference shift doesn't matter if the magnitude is small.
7. seconds_in_bucket: how stocks always perform in the same 10 seconds -> indicates possible algorithmic trading.
8. seconds_in_bucket volatility: historically how volatile the stock is in the same 10 seconds.
9. maximum bonce in x seconds: give the algo a feeling of how normal range should be
10. near price - far price: the difference of the market running auction or the market running auction + continous market trading.
11. (near price-far price)/ (far price* second in bucket): the percentage of the market running auction or the market running auction + continous market trading. indicator of market inefficiency. adjust for seconds in bucket.
12. time 0 and time 540 might be special: time 0: people may not be ready to trade, but algos are. time 540: last chance to trade.
13. spoofing: "fake orders" posted design to build order imbalance, so that it encourages the buy/sell of the stock such that it goes in the direction of the spoofer's order.
variance of the order book imbalance suggests spoofing. since we cannot cancel after 3:50, we can only do spoofing with both side large order that cancel each other out.

14. Rough fill probability: the probability for the best bid-ask price being filled. 
t=0, bid-ask price = 100-101. bid-ask vol = 1000-1000 
t=1, bid-ask price = 100-101. bid-ask vol = 500-500
then rough fill probability for bid-ask = 0.5 0.5
15. stock agreeableness: if the matching size is large relative to the order book imbalance size (compare to the cross-sectional median), then the buyer and seller agree on the price 
16. volume sitting on the order book (less best-bid-and-ask) = imbalance size - bid_size-ask_size
17. wap sitting on the order book: because wap is weighted average price for all order sitting on the order book,so we can extract parts that is not the best bid and ask price
18. best slot1 imbalance size: same calculation as imbalance size
19. difference in imbalance size: (imbalance_size-matched_size)/(matched_size+imbalance_size)
20. <s>spread: best ask price - best bid price. indicate the trading cost of crossing the spread.</s>
21. <s>spread difference: spread at time t - spread at time t-1. indicate the volatility of the spread.</s>
22. <s>spread volatility_ts: std of spread starting from first 5 observations of the day</s>
23. <s>deviation of price from the closing price (closing price is the price at second_in_basket 0) using mid price</s>
24. <s>volume imbalance at best-bid-and-ask: (bid_size-ask_size)/(bid_size+ask_size)</s>
25. <s>MOC flag: nasdaq don't accept moc order after 3:55. i.e. second in bucket >= 300</s>
26. longer memory: correlation with certain window.

    updated 2023/11/14

27. [triplet imbalance and some good factors to start](https://www.kaggle.com/code/tenghewang/stock-close-two)
28. time since last change in the imbalance_buy_sell flag
29. cross-sectional trading $ amount
30. stock-specific data: you also have access to previous days of stock performance, maybe utilize that? 
31. yesterday's target average
32. possible technical indicator like RSI, MACD, etc.
33. sectors matters. if we can do a cluster of the stocks via kmeans and if this doesnt decay too much in the testing, it can be strong
34. trade volume spike when there is news regarding the stock in the closing time. people want to trade the news. maybe a seperation / ranking in the volatility cross-section scaled by individual stock historical volatility can be helpful
35. historical median of volume of the stocks do help. [overall_med_vol](https://www.kaggle.com/code/renatoreggiani/optv-lightgbm)
36. first 5min and last 5min vol
37. some exotic highly mathematical feature for those interested [link](https://www.kaggle.com/code/hli111111/chao-detection-lyapunov-spetral-robustness-test)
38. 

### Market mechanism design induced predictive power: order allowed before market open -> looking for a better <u>BID</u> price
27. NASDAQ allows posting closing orders before the closing auction starts at 3:50. Only people looking for better execution 
price will post closing orders when the normal trading starts. so the relative volume at the first tick -> how volatile this stock is
during the normal trading time compare to other stocks
28. Also the imbalance direction for the first tick should be predictive of the day trading trend. should be buy heavy.

### academic idea: E[IO] = 0, uninformed would profit by absorbing the imbalance. 
29. Decay speed: how fast IO is decaying. -> uninformed /MM  

### some idea from the first place in [leaderboard](https://blog.csdn.net/weixin_51484067/article/details/133201087?csdn_share_tail=%7B%22type%22%3A%22blog%22%2C%22rType%22%3A%22article%22%2C%22rId%22%3A%22133201087%22%2C%22source%22%3A%22weixin_51484067%22%7D&fromshare=blogdetail) 
30. imbalance of every price types
31. imbalance of every price types to the order of 2
32. NSDAQ MOC can be seperated into 2 parts: 3:50-3:55 and 3:55-4:00. possible seperation 