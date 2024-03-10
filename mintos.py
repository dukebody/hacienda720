from csv import DictReader
from decimal import Decimal

OPERATION_ACQUISITION = "A"
OPERATION_MODIFICATION = "M"
OPERATION_CANCELLATION = "C"


## CAMBIAR ESTOS DATOS DE ABAJO
MINTOS_LOAN_BALANCES_FILE = "Mintos Investor Loan Balances 2023.csv"

# si no se ha declarado el año pasado, dejar esto como ""
MINTOS_LOAN_BALANCES_PREVIOUS_EXERCISE_FILE = "Mintos Investor Loan Balances 2023.csv"

OUTPUT_FILENAME = "test.720"
CSV_DELIMITER = ","

YEAR = "2023"
NAME = "NOMBRE APELLIDO1 APELLIDO2"
DNI = "21928208P"
PHONE = "600112233"
## CAMBIAR ESTOS DATOS DE ARRIBA


def comma_to_dot(amount):
    return amount.replace(",", ".")


def get_asset_data_from_mintos_balance_sheet(filename):
    """
    Genera la lista de assets a partir de un archivo de balance de Mintos con nombre filename
    """
    # leer archivo de Mintos a dict
    data = []
    with open(filename, "r") as file_handler:
        reader = DictReader(file_handler, delimiter=CSV_DELIMITER)
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


LINE_1 = "1720{YEAR}{DNI}{NAME:40}T{PHONE}{NAME:40}7200000000000  {n_entries:0>22} {total_amount_cents:0>17.0f} 00000000000000000                                                                                                                                                                                                                                                                                                                                \n"
LINE_N = "2720{YEAR}{DNI}{DNI}         {NAME:40}1                         V2                         LV1{isin}                                              {issuer_name:24}                 {issuer_registration_number}                                                                                                                                                                           LV00000000{operation}00000000 {amount_cents:0>14.0f} 00000000000000A{n_values_cents:0>12.0f} 10000                    \n"
def write_720_file_from_assets(filename, assets, assets_previous_exercise={}):
    """
    Escribe archivo tipo 720 con nombre filename a partir de una lista de assets
    """
    lines = [LINE_1.format(
        YEAR=YEAR, DNI=DNI, NAME=NAME, PHONE=PHONE,
        n_entries=len(assets),
        total_amount_cents=sum(asset["amount"]*100 for asset in assets.values())
    )]
    isins = set(assets.keys())
    isins_previous_exercise = set(assets_previous_exercise.keys())

    all_isins = isins | isins_previous_exercise
    new_isins = isins - isins_previous_exercise
    modified_isins = isins & isins_previous_exercise
    cancelled_isins = isins_previous_exercise - new_isins

    # generar cada línea del 720
    for isin in all_isins:
        if isin in new_isins:
            operation = OPERATION_ACQUISITION
            value = assets[isin]
            amount_cents = round(value["amount"]*100)
        elif isin in modified_isins:
            operation = OPERATION_MODIFICATION
            value = assets[isin]
            amount_cents = round(value["amount"]*100)
        elif isin in cancelled_isins:
            operation = OPERATION_CANCELLATION
            value = assets_previous_exercise[isin]
            amount_cents = 1
        else:
            raise Exception(f"Value {isin} not found!")

        if amount_cents == 0:  # en caso de menos de 1 céntimo lo redondeamos hacia arriba
            amount_cents = 1

        # el n de valores se tiene que poner con 2 decimales y cada note es 0.01€
        n_values_cents = amount_cents * 100

        line = LINE_N.format(
            YEAR=YEAR, DNI=DNI, NAME=NAME, 
            isin=isin, 
            issuer_name=value["issuer_name"],
            issuer_registration_number=value["issuer_registration_number"],
            amount_cents=amount_cents,  # el monto se tiene que poner en céntimos de €
            n_values_cents=n_values_cents,
            operation=operation,
        )
        lines.append(line)

    # guardar en archivo
    with open(filename, "w") as file_handler:
        file_handler.writelines(lines)



# cargar los activos del ejercicio a declarar
assets = get_asset_data_from_mintos_balance_sheet(MINTOS_LOAN_BALANCES_FILE)

# si hay una declaración anterior, importarla para marcar los activos como cancelados
if MINTOS_LOAN_BALANCES_PREVIOUS_EXERCISE_FILE:
    assets_previous_exercise = get_asset_data_from_mintos_balance_sheet(MINTOS_LOAN_BALANCES_PREVIOUS_EXERCISE_FILE)
else:
    assets_previous_exercise = {}


write_720_file_from_assets(OUTPUT_FILENAME, assets, assets_previous_exercise)
