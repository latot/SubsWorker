if [[ ! -f "$i" ]]; then
echo "No se encuentra: $i"
exit -1
fi

if [[ ! -f "$p" ]]; then
echo "No se encuentra: $p"
exit -1
fi

echo "Aplicando parche a $i."
xdelta3 -d -s "$i" "$p" "$d"
fi
