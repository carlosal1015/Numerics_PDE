# coding=utf-8
###-----------------------------------------------------------###
###  Name: Héctor Andrade Loarca                              ###
###  Course: Numerics of PDEs                                 ###
###  Professor: Kersten Schmidt                               ###
###                                                           ###
###               Module meshes.py                            ###
###            " Dealing with meshes "                        ###
###                                                           ###
###-----------------------------------------------------------###

import numpy as np 
import matplotlib.pyplot as plt
import scipy.sparse as sparse

#First lets define the function read_gmsh that parse a .msh file
#as input it recieve the file name

#file='square_mesh.msh'

def read_gmsh(file):
	#We read the file
	msh=open(file).read()
	#We split the big string that we get from the file by line skips \n
	msh=msh.split('\n')
	##
	#We identify the entries with Nodes by begin and end
	begin=msh.index('$Nodes')+2
	end=msh.index('$EndNodes')
	nodes=msh[begin:end]
	# We split the elements of notes by the space to get the entries
	nodes=map(lambda x:x.split(' ')[1:3],nodes)
	# Convert the entries to floats instead of strings
	p=np.array(nodes).astype(float)
	##
	#Now we identify the entries of the elements
	begin=msh.index('$Elements')+2
	end=msh.index('$EndElements')
	elements=msh[begin:end]
	#Split each element by the space between the entries
	elements=map(lambda x: x.split(' '),elements)
	##
	#We filter elements of dimension 1 and elements
	elemone=[element for element in elements if element[1]=='1']
	#We get the last two entries that represents the nodes of this one 
	#dimensional element
	elemone=[x[5:8] for x in elemone]
	#We transform to a np.array with float entries
	be=np.array(elemone).astype(int)
	#
	#We filter elements of dimension 2 and elements
	elemtwo=[element for element in elements if element[1]=='2']
	#We get the last three entries that represents the nodes of this two
	#dimensional element that is a triangle in counterclockwise order
	elemtwo=[x[5:9] for x in elemtwo]
	#We transform to a np.array with float entries
	t=np.array(elemtwo).astype(int)
	#Finally we return a list of this 3 arrays
	return [p,t,be]

#Now lets define a fucntion grid_square that produces a uniform grid of
# a square of side length a and maximal mesh widht h0, with the same outputs
# as read_gmsh

# If we want h0 to be the maximal mesh width in the square of lenght side a
# we need it to be an hypotenouse of a right triangle with equal sides that 
# are divisors of the length a, to fit perfectly 

# Thats it n*(h0)/sqrt(2)=a for some n

# Lets define the fuction grid_square
#a=1
#h0=np.sqrt(2)/10

def grid_square(a,h0):
	#Check if h0 and a fullfill the requirements for regular meshes
	if int(np.sqrt(2)*a/h0)!=np.sqrt(2)*a/h0:
		return "h0 and a do not generate a regular mesh"
	else:
		#Define the number of elements in each side
		n=int(np.sqrt(2)*a/h0)
		#We gonna order the nodes from below to the top beginnign ant the 0,0
		p=[[i*a/float(n),0.0] for i in range(0,n+1)]
		for j in range(1,n+1):
			p=p+[[i*a/float(n),j*a/float(n)] for i in range(0,n+1)]
		#We convert p to np.array
		p=np.array(p)
		##
		# Now we generate the arrays with the one dimensional elements in the border
		# We will take the nodes numerate from bellow to the top of the square grid
		# And we will take the elements in the border in counterclockwise order
		# Divided in the 4 borders
		#First border
		first=[[i,i+1] for i in range(1,n+1)]
		second= [[(n+1)*i,(n+1)*i+n+1] for i in range(1,n+1)]
		third=[[(n+1)**2-i+1,(n+1)**2-i] for i in range(1,n+1)]
		fourth=[[(n+1)**2-n-(i-1)*(n+1),(n+1)**2-n-i*(n+1)] for i in range(1,n+1)]
		#We join the borders and convert to np-array
		be=np.array(first+second+third+fourth)
		##
		# Now we gonna create the arrays with the two dimensional triangles elements 
		# nodes
		# We gonna create them in layers from bellow to top
		# We create the two type of triangles depending on the orientation of the triangle
		# First the triangles pointing down-left
		j=1
		t1=[[i+(j-1)*(n+1),i+1+(j-1)*(n+1),(i+1)+(n+1)+(j-1)*(n+1)] for i in range(1,n+1)]
		for j in range(2,n+1):
			t1=t1+[[i+(j-1)*(n+1),i+1+(j-1)*(n+1),(i+1)+(n+1)+(j-1)*(n+1)] for i in range(1,n+1)]
		# Now the triangles pointing up-right
		j=1
		t2=[[i+(j-1)*(n+1),i+1+(n+1)+(j-1)*(n+1),i+(n+1)+(j-1)*(n+1)] for i in range(1,n+1)]
		for j in range(2,n+1):
			t2=t2+[[i+(j-1)*(n+1),i+1+(n+1)+(j-1)*(n+1),i+(n+1)+(j-1)*(n+1)] for i in range(1,n+1)]
		#And then we join q1 and q2 and convert it to np.array
		t=np.array(t1+t2)
		# Now we got our three outputs
		return [p,t,be]

#Now lets define a function that draws the mesh with Matplotlib which accepts
# a numpy array p with the nodes and an array t of the triangles with the index 
# of the nodes and the filename that you want to save the image and the title

def show(p,t,file_name,title):
	# Create the loop over each triangle
	for i in range(0,len(t)):
		ti=t[i]
		# Take the points of each triangle
		pi=[p[ti[i]-1] for i in range(0,3)]
		#Define the x and y coordinates of each point
		xi=[xi[0] for xi in pi]
		yi=[yi[1] for yi in pi]
		#Close the loop in the triangle
		xi=xi+[xi[0]]
		yi=yi+[yi[0]]
		#plot each trianle
		plt.plot(xi,yi,"-k")
	plt.title(title)
	plt.xlabel('x1')
	plt.ylabel('y2')
	plt.savefig(file_name)
	plt.close()

# Now lets define a maximal mesh function that returns the maximal width
# Of a mesh with p nodes and t triangles

def max_mesh_width(p,t):
	# We save in a array the maximum distance between points in each triangle
	h=[]
	for i in range(0,len(t)):
		ti=t[i]
		# Take the points of each triangle
		pi=[p[ti[i]-1] for i in range(0,3)]
		maxi=max([np.linalg.norm(pi[0]-pi[1]),np.linalg.norm(pi[0]-pi[2]),np.linalg.norm(pi[1]-pi[2])])
		h.append(maxi)
	#Finally we get the maximum width of the mesh
	return max(h)

# Now lets define a function that compute the global stiffness matrix
# in sparse format

# input:
# p - Nx2 matrix with coordinates of the nodes
# t - Mx3 matrix with indices of nodes of the triangles

# First for each triangle lets define a function that produce its
# TK in its sparse lil format

# input:
# 

