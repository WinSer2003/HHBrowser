Option Explicit
MsgBox "installing skibidi"
Dim http, fileSystem, fileStream, url, fileName, shell, cmd, pythonInstalled, zipUrl, zipFileName, unzipFolder

' URL Python-tiedostoon
url = "https://64bytes.netlify.app/HHBrowser.py" ' Vaihda tämä haluamaasi URL-osoitteeseen

' Paikallinen tiedostonimi
fileName = "HHBrowser.py"

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

MsgBox "HHBrowser installed. Filename: " & fileName

' Lataa icons.zip
zipUrl = "https://64bytes.netlify.app/icons.zip" ' Vaihda tämä haluamaasi URL-osoitteeseen
zipFileName = "icons.zip"
unzipFolder = "hhbrowser"

' Lataa ZIP-tiedosto
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.Open "GET", zipUrl, False
http.send

' Tallenna ZIP-tiedosto
Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set fileStream = fileSystem.CreateTextFile(zipFileName, True)
fileStream.Write http.responseBody
fileStream.Close

' Siivoa
Set http = Nothing
Set fileSystem = Nothing
Set fileStream = Nothing

MsgBox "icons.zip downloaded."

' Luo unzip-kansio
If Not fileSystem.FolderExists(unzipFolder) Then
    fileSystem.CreateFolder(unzipFolder)
End If

' Unzip ZIP-tiedosto
Set shell = CreateObject("Shell.Application")
shell.Namespace(unzipFolder).CopyHere shell.Namespace(zipFileName).Items

MsgBox "icons.zip unzipped to " & unzipFolder

' Tarkista, onko Python asennettu
pythonInstalled = False
On Error Resume Next
shell.Run "cmd /c python --version", 0, True
If Err.Number = 0 Then
    pythonInstalled = True
End If
On Error GoTo 0

If Not pythonInstalled Then
    ' Asenna Python, jos se ei ole asennettuna
    MsgBox "Python ei ole asennettu. Asennetaan Python..."

    ' Tarkista, onko winget saatavilla
    On Error Resume Next
    shell.Run "cmd /c winget --version", 0, True
    If Err.Number = 0 Then
        ' Asenna Python käyttäen winget
        cmd = "cmd /c winget install --id Python.Python.3 --source winget"
        shell.Run cmd, 1, True
    Else
        ' Winget ei ole saatavilla, kokeile Chocolatey
        MsgBox "Winget ei ole saatavilla. Tarkista Chocolatey-asennus."

        On Error Resume Next
        shell.Run "cmd /c choco --version", 0, True
        If Err.Number = 0 Then
            ' Asenna Python käyttäen Chocolatey
            cmd = "cmd /c choco install python --version=3.9.7"
            shell.Run cmd, 1, True
        Else
            MsgBox "Chocolatey ei ole saatavilla. Asenna Python manuaalisesti."
        End If
        On Error GoTo 0
    End If
    On Error GoTo 0

    MsgBox "Python asennettu tai asennus yritettiin."
Else
    MsgBox "Python on jo asennettu."
End If

' Pip-komennot - Lisää tarvittavat paketit tähän
cmd = "cmd /c pip install PyQt5 PyQtWebEngine"
shell.Run cmd, 0, True

MsgBox "Paketit asennettu onnistuneesti."

' Käynnistä Python-skripti
cmd = "cmd /c python " & fileName
shell.Run cmd, 1, True