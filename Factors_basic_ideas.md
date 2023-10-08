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
8. 
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
