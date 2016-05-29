
xor=lambda x, y: not(x and y) and (x or y)
div=lambda x, y: abs(x)//abs(y) if xor(x<0, y>0) else -(abs(x)//abs(y))
mod=lambda x, y: -(-x%abs(y)) if x<0 else x%abs(y)
