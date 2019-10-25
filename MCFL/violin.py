import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
 
def blob_plot(ax,data,list_pos, extra=False):
    lextra=[]
    for d,p in zip(data,list_pos):
      
      #this makes the histogram that constitutes the blob plot
      m=min(d)
      M=max(d)
      nbins=20
      x = np.linspace(m,M,nbins) # support for histogram
      his,bins = np.histogram(d, bins=nbins)
      
      #scale the histogram to a proper size (you may have to fiddle with this), then place it at position 'pos'
      scale_blob=2.
      shift_his_plus_pos =  [ p + h*scale_blob/float(len(d))  for h in his]
      shift_his_minus_pos = [ p - h*scale_blob/float(len(d))  for h in his]
      
      facecolor,alpha=color_alpha_blobs # assign color and transparency
      #this is the matplotlib function that does the trick
      ax.fill_betweenx(x,shift_his_minus_pos, shift_his_plus_pos, linewidth=0.0, facecolor= facecolor, alpha=alpha)
      #calculates median or mean, if you want
      if extra=='median': lextra.append( np.median(d) )
      elif extra=='mean': lextra.append( np.mean(d) )
    #and plots it
    if extra != False:
      color = 'orangered'
      ax.plot(list_pos,lextra, color=color_mean_or_median,linestyle='-',marker='D',markersize=5, lw=1.5)
      
 
# MAKE UP SOME DATA
list_positions=[0,1,2,3]#this is their position on the x-axis
file_name = ['out_ochiai', 'out_barinel', 'out_jaccard', 'out_dstar']
data_for_blobplot=[]	
# this will contain a list for each blob we want in the plot
extra='median'
for pos in list_positions:
  #if pos <= 2: some_data = np.random.gumbel(pos,1, 1000) 	# generate some data 
  #else: some_data = np.random.normal(pos,1, 1000)		# generate some other data
  input_file = open(file_name[pos], 'r')
  data_list = []
  for line in input_file:
      if line.startswith('avg:'):
          continue
      info_now = line.split(' ')
      try:
          value = float(info_now[-1])/2.0
          # print(value)
          data_list.append(value)
      except Exception as e:
          print(e)
  data_for_blobplot.append(np.array(data_list))				# and append it to the list
 
# PLOTTING 
color_alpha_blobs=('midnightblue',0.7)			#this is the color of the blobplot
color_mean_or_median='orangered'			#this is the colot of the median or mean, whatever you specify
fig = plt.figure()					# makes a figure
ax = fig.add_subplot(111)				# adds a single subplot
 
#this is the blobplotting function
blob_plot(ax, data_for_blobplot, list_pos=list_positions, extra=extra)	#makes blob plots, if extra is not spcified, makes no median/mean
 
 
ax.set_xlim(-1., len(list_positions)) #to display all of them
ax.set_ylim(-1.2, 1.2) 
plt.title('Beautiful blob plots',fontsize=18)
plt.xlabel('$\mu$ (yup, that is Latex)', fontsize=14)
plt.ylabel('distribution of my variable', fontsize=14)
 
####################################################
# So far this is all you need to make the blob plot
# Below is if you want a legend for the medain/mean
####################################################
 
# draw temporary dot to use it for a legend, later set to invisible
h = ax.scatter( [1],[1], marker='D', color=color_mean_or_median, label='extra')
#draws the legend, with larger symbols
leg=plt.legend(loc= 'upper left',scatterpoints=1)	
for legobj in leg.legendHandles:
  legobj.set_linewidth(10.0)
h.set_visible(False)
 
plt.savefig('blobplot.png') 	# saving to png, alternatively you can write 'blobplot.pdf', or other formats
plt.show()	
