

Option Explicit

Dim http, fileSystem, fileStream, url, fileName

' URL Python-tiedostoon
url = "https://example.com/your_script.py" ' Vaihda tämä haluamaasi URL-osoitteeseen

' Paikallinen tiedostonimi
fileName = "downloaded_script.py"

' Luo XMLHTTP-objekti tiedoston lataamiseen
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.Open "GET", url, False
http.send

' Luo FileSystem-objekti tiedoston tallentamiseen
Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set fileStream = fileSystem.CreateTextFile(fileName, True)

' Kirjoita ladattu sisältö tiedostoon
fileStream.Write http.responseText
fileStream.Close

' Siivoa
Set http = Nothing
Set fileSystem = Nothing
Set fileStream = Nothing

MsgBox "HHBrowser on asennettu  " & fileName
