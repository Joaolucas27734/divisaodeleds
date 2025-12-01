function dividirLeads50_50() {
  const sheetName = "Total";     // Nome da aba
  const classificacaoCol = 7;    // Coluna G = 7
  const responsavelCol = 8;      // Coluna H = onde será escrito Vendedor A / B
  
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName(sheetName);
  const lastRow = sheet.getLastRow();

  // Lê todos os dados
  const data = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).getValues();

  // Organiza por classificação
  const grupos = {};

  data.forEach((row, i) => {
    const classificacao = row[classificacaoCol - 1];

    if (!grupos[classificacao]) {
      grupos[classificacao] = [];
    }

    grupos[classificacao].push({
      index: i + 2,     // número da linha na planilha
      dados: row
    });
  });

  // Para cada classificação → embaralha → divide 50/50
  for (let categoria in grupos) {

    let lista = grupos[categoria];

    // Embaralhar (shuffle)
    lista.sort(() => Math.random() - 0.5);

    const metade = Math.floor(lista.length / 2);

    // Primeira metade → Vendedor A
    lista.slice(0, metade).forEach(item => {
      sheet.getRange(item.index, responsavelCol).setValue("Vendedor A");
    });

    // Segunda metade → Vendedor B
    lista.slice(metade).forEach(item => {
      sheet.getRange(item.index, responsavelCol).setValue("Vendedor B");
    });
  }

  SpreadsheetApp.flush();
  Logger.log("Divisão concluída!");
}
