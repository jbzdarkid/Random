config = {
	'RaceTracker': {
		'Scan Rate': 30, # Frequency of scans for image comparison. This is 10x faster than default.
		'Accuracy': 10, # Frequency of photos to use for comparison.
		'Redundancy': 2, # Number of times to check for a certain runner delay.
		# Also effects timeliness of information. If a runner is 10 minutes behind, and this value is at 2,
		# then this information will be discovered after 20 minutes.
	}
}