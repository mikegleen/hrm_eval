# Remove the xmlns declaration from the kml node.
/<kml/{$0 = "<kml>";}
	{print;}
