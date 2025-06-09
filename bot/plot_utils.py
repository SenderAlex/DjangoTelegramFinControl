from aiogram import Router
import matplotlib.pyplot as plt


router = Router()


def plot_pie(data, title):
    plt.figure(figsize=(6, 6))
    data.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.title(title)
    plt.axis('equal')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path, format='png')
    plt.close()
    return file_path


def plot_bar(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 11))
    data.plot.bar()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path


def plot_category_bar(data, title, xlabel, ylabel):
    plt.figure(figsize=(8, 11))
    data.plot.bar()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title='Категории', bbox_to_anchor=(1.05, 1), loc='upper left')
    file_path = f'{title}.png'
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path
