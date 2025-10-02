function exportFileMap() {
  var folderId = "1VuY6jM-a8UJi4hHs1sJ6z30O2dYjksl1"; // Replace with your Google Drive folder ID
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();

  var csvLines = [];
  csvLines.push(["userid","fileid"]);

  while (files.hasNext()) {
    var file = files.next();
    var name = file.getName(); // e.g., "deivjt.pdf"
    var userid = name.replace(/\.[^/.]+$/, ""); // remove extension
    var fileId = file.getId();
    csvLines.push([userid, fileId]);
  }

  var csvContent = csvLines.map(row => row.join(",")).join("\n");
  DriveApp.createFile('file_map.csv', csvContent, MimeType.PLAIN_TEXT);
  Logger.log("file_map.csv created in Drive root.");
}
