from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ContentType, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



from aiogram_dialog import (
    Dialog, DialogManager, StartMode, Window,
)
from aiogram_dialog.widgets.kbd import Checkbox
from aiogram_dialog.widgets.text import Const

import app.keyboards as kb
from app.parcer import  proverka_ks, pars_zakupki

router = Router()



check1 = Checkbox(Const("Совпадение наименования закупки с ТЗ: ✅"), Const('Совпадение наименования закупки с ТЗ: ❌'), id="rule1", default=True)
check2 = Checkbox(Const("Обеспечение исполнения контракта: ✅"), Const('Обеспечение исполнения контракта: ❌'), id="rule2", default=True)
check3 = Checkbox(Const("Наличие сертификатов/лицензий: ✅"), Const('Наличие сертификатов/лицензий: ❌'), id="rule3", default=True)
check4 = Checkbox(Const("График и этап поставки: ✅"), Const('График и этап поставки: ❌'), id="rule4", default=True)
check5 = Checkbox(Const("Максимальное значение цены контракта: ✅"), Const('Максимальное значение цены контракта: ❌'), id="rule5", default=True)
check6 = Checkbox(Const("Проверки при наличии ТЗ: ✅"), Const('Проверки при наличии ТЗ: ❌'), id="rule6", default=True)




class NewData(StatesGroup):
    SessionNumber = State()
    CheckStatus = State()
    AcceptStatus = State()
    WaitAfter = State()

class MySG(StatesGroup):
    main = State()


main_window = Window(
    Const('Список критериев:'),
    check1,
    check2,
    check3,
    check4,
    check5,
    check6,
    state=MySG.main,
)





dialog = Dialog(main_window)


async def save_checkbox_state(dialog_manager: DialogManager, state: FSMContext):
    bool_data = {
        "rule1": check1.is_checked(dialog_manager),
        "rule2": check2.is_checked(dialog_manager),
        "rule3": check3.is_checked(dialog_manager),
        "rule4": check4.is_checked(dialog_manager),
        "rule5": check5.is_checked(dialog_manager),
        "rule6": check6.is_checked(dialog_manager),
    }
    await state.update_data(bool_data=bool_data)


async def load_checkbox_state(state: FSMContext):
    data = await state.get_data()
    bool_data = data.get("bool_data", {})
    check1.default = bool_data.get("rule1", True)
    check2.default = bool_data.get("rule2", True)
    check3.default = bool_data.get("rule3", True)
    check4.default = bool_data.get("rule4", True)
    check5.default = bool_data.get("rule5", True)
    check6.default = bool_data.get("rule6", True)


async def reset_checkboxes(state: FSMContext):
    await state.update_data(bool_data={})  # Очистка сохраненного состояния
    check1.default = True
    check2.default = True
    check3.default = True
    check4.default = True
    check5.default = True
    check6.default = True



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Для того, чтобы перейти к вводу номера котировочной сессии, нажмите "Начать"', reply_markup=kb.start)

@router.callback_query(F.data == 'start')
async def started(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewData.SessionNumber)
    await callback.answer('Успешно начато')
    await callback.message.answer('Введите номер котировочной сессии:')


@router.message(F.text == 'Отменить ввод')
async def cancel_input(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await reset_checkboxes(state)
        await message.reply('Ввод отменен.', reply_markup=ReplyKeyboardRemove())
        await cmd_start(message)
    else:
        await message.reply("Нет активного ввода для отмены.")

@router.message(F.text == 'Вывести спецификацию текущей котировочной сессии')
async def cancel_input(message: Message, state: FSMContext):
    current_state = await state.get_state()
    valid_states = ["NewData:AcceptStatus", "NewData:CheckStatus", "NewData:WaitAfter"]
    if current_state not in valid_states:
        await message.answer('Нет введенного номера котировочной сессии')
    else:
        data = await state.get_data()
        session_number = data.get('session_number')
        await message.answer("Информация:")
        name,isElectronicContractExecutionRequired,isContractGuaranteeRequired,licenseFiles,customer_name,federalLawName,startDate,endDate,startCost,nextCost,name_docx,doc_docx,name_pdf,doc_pdf = pars_zakupki(session_number)
        prompt1 = f"Наименование закупки: {name}, "
        await message.answer(prompt1)
@router.message()
async def handle_input(message: Message, state: FSMContext, dialog_manager: DialogManager):
    current_state = await state.get_state()
    session_number = ''
    match current_state:
        case None:
            if message.content_type == ContentType.TEXT:
                await message.reply('Вы ввели что-то некорректное.')
            else:
                await message.reply('Вы ввели что-то некорректное.')
        case NewData.SessionNumber:
            if message.content_type == ContentType.TEXT and message.text.isdigit():
                await state.set_state(NewData.CheckStatus)
                await message.answer('Выберите критерии отбора котировочной сессии:', reply_markup=kb.main)
                await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)
                session_number = message.text
                await state.update_data(session_number=session_number)
                print(f"Номер котировочной сессии: {message.text}") 
            else:
                await message.reply('Пожалуйста, введите числовое значение для номера котировочной сессии')
        case NewData.CheckStatus:
            if message.text == 'Подтвердить критерии':
                await save_checkbox_state(dialog_manager, state)
                # Получаем сохранённые данные из состояния
                data = await state.get_data()
                bool_data = data.get('bool_data', {})
                # Собираем список подтверждённых критериев
                confirmed_criteria = [
                    text for checkbox, text in zip(
                        bool_data.values(),
                        [
                            "Совпадение наименования закупки с ТЗ",
                            "Обеспечение исполнения контракта",
                            "Наличие сертификатов/лицензий",
                            "График и этап поставки",
                            "Максимальное значение цены контракта",
                            "Проверки при наличии ТЗ"
                        ]
                    ) if checkbox
                ]

                print("Подтверждённые критерии:")
                for criterion in confirmed_criteria:
                    print(f"- {criterion}")

                await state.set_state(NewData.WaitAfter)
                await message.answer(
                    'Вы подтвердили критерии:\n' + '\n'.join(f"- {c}" for c in confirmed_criteria),
                    reply_markup=kb.main2
                )
            elif message.content_type == ContentType.TEXT:
                await message.reply('Вы ввели что-то некорректное.')
            else:
                await message.reply('Вы ввели что-то некорректное.')
        case NewData.WaitAfter:
            if message.text == 'Запустить проверку по данной котировочной сессии':
                data = await state.get_data()
                session_number = data.get('session_number')
                if not session_number:
                    await message.reply("Номер котировочной сессии не найден. Пожалуйста, введите номер сессии заново.")
                    return
                bool_data = data.get('bool_data', {})
                p1 = bool_data.get("rule1", False)
                p2 = bool_data.get("rule2", False)
                p3 = bool_data.get("rule3", False)
                p4 = bool_data.get("rule4", False)
                p5 = bool_data.get("rule5", False)
                p6 = bool_data.get("rule6", False)
                print(f"Запуск проверки для котировочной сессии: {session_number}")
                print(f"Выбранные критерии: p1={p1}, p2={p2}, p3={p3}, p4={p4}, p5={p5}, p6={p6}")
                try:
                    result = proverka_ks(session_number, p1, p2, p3, p4, p5, p6)
                    if result:
                        await message.answer("Проверка успешно выполнена: все критерии соблюдены ✅", reply_markup=ReplyKeyboardRemove())
                    else:
                        await message.answer("Проверка завершена: найдены несоответствия ❌", reply_markup=ReplyKeyboardRemove())
                except Exception as e:
                    await message.answer(f"Произошла ошибка при выполнении проверки: {e}", reply_markup=ReplyKeyboardRemove())

                await message.answer('Успешно проверено.', reply_markup=ReplyKeyboardRemove())
                await state.clear()
                await reset_checkboxes(state)
                await cmd_start(message)
            elif message.text == 'Внести изменения в критерии':
                await load_checkbox_state(state)
                await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)
                await state.set_state(NewData.CheckStatus)
                await message.answer('Пожалуйста, внесите все необходимые изменения и нажмите "Подтвердить критерии"', reply_markup=kb.main)
            elif message.content_type == ContentType.TEXT:
                await message.reply('Вы ввели что-то некорректное.')
            else:
                await message.reply('Вы ввели что-то некорректное.')           