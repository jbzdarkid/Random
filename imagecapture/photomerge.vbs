Dim appRef
Set appRef = CreateObject( "PhotoshopElements.Application" )

' Create a new 2x4 inch document and assign it to a variable.
Dim docRef
Set docRef = appRef.Documents.Add(2, 4)

Call MakePhotoMerge("a", "b", "c", "d")

'docRef.SaveAs("C:\Users\localhost\Documents\Github\Random\imagecapture\TestFile", "bmp")