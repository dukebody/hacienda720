from csv import DictReader
from decimal import Decimal


# Cambiar estos datos
INPUT_FILENAME = "Mintos Investor Loan Balances on Specific Date.xlsx.csv"
OUTPUT_FILENAME = "test.720"

YEAR = "2022"
NAME = "NOMBRE APELLIDO1 APELLIDO2"
DNI = "21928208P"
PHONE = "600112233"



def comma_to_dot(amount):
    return amount.replace(",", ".")


def get_asset_data_from_mintos_balance_sheet(filename):
    """
    Genera la lista de assets a partir de un archivo de balance de Mintos con nombre filename
    """
    # leer archivo de Mintos a dict
    data = []
    with open(filename, "r") as file_handler:
        reader = DictReader(file_handler)
        data = [row for row in reader]
    # generar datos de cada valor
    assets = {}
    for loan in data:
        # si el isin ya está en el diccionario, añadir el monto
        if loan["ISIN"] in assets:
            assets[loan["ISIN"]]["amount"] += Decimal(comma_to_dot(loan["Outstanding investments LOC"]))
        else:
            assets[loan["ISIN"]] = {
                "amount": Decimal(comma_to_dot(loan["Outstanding investments LOC"])),
                "issuer_name": loan["Issuer name"],
                "issuer_registration_number": loan["Issuer registration number"]
                }

    return assets

LINE_1 = "1720{YEAR}{DNI}{NAME:40}T{PHONE}{NAME:40}7200000000000  {n_entries:0>22} {total_amount:0>17.0f} 00000000000000000                                                                                                                                                                                                                                                                                                                                \n"
LINE_N = "2720{YEAR}{DNI}{DNI}         {NAME:40}1                         V2                         LV1{isin}                                              {issuer_name:24}                 {issuer_registration_number}                                                                                                                                                                           LV00000000A00000000 {amount:0>14.0f} 00000000000000A{n_notes:0>12.0f} 10000                    \n"
def write_720_file_from_assets(assets, filename):
    """
    Escribe archivo tipo 720 con nombre filename a partir de una lista de assets
    """
    # generar cada línea del 720
    lines = [LINE_1.format(
        YEAR=YEAR, DNI=DNI, NAME=NAME, PHONE=PHONE,
        n_entries=len(assets),
        total_amount=sum(asset["amount"]*100 for asset in assets.values())
    )]
    for isin, value in assets.items():
        line = LINE_N.format(
            YEAR=YEAR, DNI=DNI, NAME=NAME, 
            isin=isin, 
            issuer_name=value["issuer_name"],
            issuer_registration_number=value["issuer_registration_number"],
            amount=value["amount"]*100,
            n_notes=value["amount"]*10000,)
        lines.append(line)

    # guardar en archivo
    with open(filename, "w") as file_handler:
        file_handler.writelines(lines)


assets = get_asset_data_from_mintos_balance_sheet(INPUT_FILENAME)
write_720_file_from_assets(assets, OUTPUT_FILENAME)
